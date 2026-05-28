"""
Phase 5: OpenVINO Export
Convert PyTorch model to OpenVINO IR format and benchmark
"""
import torch
import torch.nn as nn
import time
import numpy as np
from pathlib import Path

try:
    from openvino.runtime import Core, Type, get_version
    OPENVINO_AVAILABLE = True
except ImportError:
    OPENVINO_AVAILABLE = False
    print('Warning: OpenVINO not installed. Install with: pip install openvino')


def convert_to_openvino(model, input_shape=(1, 2), export_dir=None,
                        precision='FP16', verbose=True):
    """
    Convert PyTorch model to OpenVINO IR format
    
    Args:
        model: PyTorch ResMLP model
        input_shape: Input tensor shape (batch_size, feature_dim)
        export_dir: Where to save OpenVINO IR files
        precision: 'FP32' or 'FP16'
        verbose: Print logs
        
    Returns:
        str: Path to converted model
    """
    if export_dir is None:
        project_root = Path(__file__).resolve().parent.parent
        export_dir = str(project_root / 'models' / 'openvino')
    if not OPENVINO_AVAILABLE:
        print('OpenVINO not available. Skipping conversion.')
        return None
    
    Path(export_dir).mkdir(parents=True, exist_ok=True)
    
    # Create dummy input
    dummy_input = torch.randn(input_shape)
    
    # Convert to ONNX first (intermediate format)
    onnx_path = os.path.join(export_dir, 'model.onnx')
    
    try:
        torch.onnx.export(
            model,
            dummy_input,
            onnx_path,
            input_names=['positions'],
            output_names=['beams'],
            dynamic_axes={
                'positions': {0: 'batch_size'},
                'beams': {0: 'batch_size'}
            },
            opset_version=12
        )
        if verbose:
            print(f'[OK] ONNX model exported to {onnx_path}')
    except Exception as e:
        print(f'Error converting to ONNX: {e}')
        return None
    
    # Convert ONNX to OpenVINO IR
    try:
        from openvino.tools import mo
        
        ir_path = os.path.join(export_dir, 'model')
        
        # Use mo.convert_model for newer OpenVINO versions
        try:
            ov_model = mo.convert_model(onnx_path, compress_to_fp16=(precision == 'FP16'))
            ov_model.save_model(ir_path)
        except:
            # Fallback for older versions
            print('Note: Using standard conversion (may require CLI for FP16)')
            ov_model = mo.convert_model(onnx_path)
            ov_model.save_model(ir_path)
        
        if verbose:
            print(f'[OK] OpenVINO IR model saved to {ir_path}')
            print(f'  - {ir_path}.xml')
            print(f'  - {ir_path}.bin')
        
        return ir_path
    
    except Exception as e:
        print(f'Error converting to OpenVINO IR: {e}')
        print('Attempting alternative export...')
        return None


def benchmark_pytorch_cpu(model, num_inferences=1000, batch_size=1, device='cpu'):
    """
    Benchmark PyTorch model on CPU
    
    Args:
        model: PyTorch model
        num_inferences: Number of inference iterations
        batch_size: Batch size for inference
        device: 'cpu' or 'cuda'
        
    Returns:
        dict: Latency statistics (ms)
    """
    model.eval()
    model.to(device)
    
    # Warmup
    with torch.no_grad():
        for _ in range(10):
            x = torch.randn(batch_size, 2, device=device)
            _ = model(x)
    
    # Benchmark
    latencies = []
    
    with torch.no_grad():
        for _ in range(num_inferences):
            x = torch.randn(batch_size, 2, device=device)
            
            start = time.perf_counter()
            _ = model(x)
            end = time.perf_counter()
            
            latencies.append((end - start) * 1000)  # Convert to ms
    
    latencies = np.array(latencies)
    
    stats = {
        'mean': np.mean(latencies),
        'std': np.std(latencies),
        'min': np.min(latencies),
        'max': np.max(latencies),
        'p50': np.percentile(latencies, 50),
        'p99': np.percentile(latencies, 99)
    }
    
    return stats


def benchmark_openvino(ir_path, num_inferences=1000, batch_size=1):
    """
    Benchmark OpenVINO model (CPU or GPU)
    
    Args:
        ir_path: Path to OpenVINO IR model
        num_inferences: Number of inference iterations
        batch_size: Batch size
        
    Returns:
        dict: Latency statistics (ms)
    """
    if not OPENVINO_AVAILABLE:
        return None
    
    try:
        from openvino.runtime import Core
        
        # Load model
        core = Core()
        model = core.read_model(ir_path + '.xml')
        
        # Try to compile on GPU if available, otherwise CPU
        try:
            compiled_model = core.compile_model(model, device_name='GPU')
            device_used = 'GPU (Intel Iris Xe)'
        except:
            compiled_model = core.compile_model(model, device_name='CPU')
            device_used = 'CPU'
        
        # Get input/output names
        input_name = compiled_model.input(0).any_name
        output_name = compiled_model.output(0).any_name
        
        # Warmup
        for _ in range(10):
            input_data = np.random.randn(batch_size, 2).astype(np.float32)
            compiled_model([input_data])
        
        # Benchmark
        latencies = []
        
        for _ in range(num_inferences):
            input_data = np.random.randn(batch_size, 2).astype(np.float32)
            
            start = time.perf_counter()
            compiled_model([input_data])
            end = time.perf_counter()
            
            latencies.append((end - start) * 1000)
        
        latencies = np.array(latencies)
        
        stats = {
            'device': device_used,
            'mean': np.mean(latencies),
            'std': np.std(latencies),
            'min': np.min(latencies),
            'max': np.max(latencies),
            'p50': np.percentile(latencies, 50),
            'p99': np.percentile(latencies, 99)
        }
        
        return stats
    
    except Exception as e:
        print(f'Error benchmarking OpenVINO: {e}')
        return None


def compare_runtimes(model, ir_path=None, num_inferences=1000, verbose=True):
    """
    Compare PyTorch vs OpenVINO inference latency
    
    Args:
        model: PyTorch model
        ir_path: Path to OpenVINO IR model (optional)
        num_inferences: Number of inferences for benchmark
        verbose: Print results
        
    Returns:
        dict: Comparison results
    """
    if verbose:
        print('\n' + '='*60)
        print('INFERENCE PERFORMANCE COMPARISON')
        print('='*60)
    
    results = {}
    
    # PyTorch benchmark
    pytorch_stats = benchmark_pytorch_cpu(model, num_inferences, device='cpu')
    results['pytorch_cpu'] = pytorch_stats
    
    if verbose:
        print(f'\nPyTorch (CPU):')
        print(f'  Mean latency: {pytorch_stats["mean"]:.4f} ms')
        print(f'  P50: {pytorch_stats["p50"]:.4f} ms, P99: {pytorch_stats["p99"]:.4f} ms')
    
    # OpenVINO benchmark
    if ir_path and OPENVINO_AVAILABLE:
        ov_stats = benchmark_openvino(ir_path, num_inferences)
        if ov_stats:
            results['openvino'] = ov_stats
            
            if verbose:
                print(f'\nOpenVINO ({ov_stats["device"]}):')
                print(f'  Mean latency: {ov_stats["mean"]:.4f} ms')
                print(f'  P50: {ov_stats["p50"]:.4f} ms, P99: {ov_stats["p99"]:.4f} ms')
                
                speedup = pytorch_stats['mean'] / ov_stats['mean']
                print(f'\nSpeedup (PyTorch → OpenVINO): {speedup:.2f}x')
    
    return results


if __name__ == '__main__':
    print('Phase 5: OpenVINO Export')
    print('-' * 50)
    print('(Use with loaded PyTorch model)')


import os
