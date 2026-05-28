"""
Data Validation & Diagnostics Script
Checks system setup and data availability before running pipeline
"""
import os
import sys
import platform
import torch
import numpy as np
from pathlib import Path

def check_system():
    """Check system information and Python environment"""
    print('='*70)
    print('SYSTEM INFORMATION')
    print('='*70)
    
    print(f'OS: {platform.system()} {platform.release()}')
    print(f'Python: {platform.python_version()}')
    print(f'Platform: {platform.machine()}')
    
    # CPU info
    try:
        import psutil
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq().current if hasattr(psutil.cpu_freq(), 'current') else 'N/A'
        print(f'CPU Cores: {cpu_count}')
        print(f'CPU Frequency: {cpu_freq} MHz')
        print(f'Memory: {psutil.virtual_memory().total / 1e9:.1f} GB')
    except:
        print('CPU/Memory info not available')
    
    print()


def check_libraries():
    """Check if required libraries are installed"""
    print('='*70)
    print('LIBRARY CHECK')
    print('='*70)
    
    libraries = {
        'torch': 'PyTorch',
        'numpy': 'NumPy',
        'scipy': 'SciPy',
        'matplotlib': 'Matplotlib',
        'sklearn': 'Scikit-Learn'
    }
    
    missing = []
    
    for lib_name, lib_display in libraries.items():
        try:
            module = __import__(lib_name)
            version = getattr(module, '__version__', 'Unknown')
            print(f'[OK] {lib_display:20s} {version}')
        except ImportError:
            print(f'[FAIL] {lib_display:20s} NOT INSTALLED')
            missing.append(lib_name)
    
    # OpenVINO (optional but recommended)
    try:
        from openvino import get_version
        version = get_version()
        print(f'[OK] OpenVINO           {version}')
    except ImportError:
        print(f'[WARN] OpenVINO          NOT INSTALLED (optional)')
    
    print()
    
    if missing:
        print(f'Missing libraries: {", ".join(missing)}')
        print(f'Install with: pip install {" ".join(missing)}')
        return False
    
    return True


def check_data_files():
    """Check for input data files"""
    print('='*70)
    print('DATA FILES CHECK')
    print('='*70)
    
    project_root = Path(__file__).resolve().parent.parent
    _downloads = Path(os.environ.get("DOWNLOADS_DIR", Path.home() / "Downloads"))
    files_to_check = {
        'NY Zip': str(project_root / 'city_0_newyork_3p5.zip') if (project_root / 'city_0_newyork_3p5.zip').exists() else str(_downloads / 'city_0_newyork_3p5.zip'),
        'LA Zip': str(project_root / 'city_1_losangeles_3p5.zip') if (project_root / 'city_1_losangeles_3p5.zip').exists() else str(_downloads / 'city_1_losangeles_3p5.zip')
    }
    
    found_all = True
    total_size = 0
    
    for name, path in files_to_check.items():
        path_obj = Path(path)
        if path_obj.exists():
            size_gb = path_obj.stat().st_size / 1e9
            total_size += path_obj.stat().st_size
            print(f'[OK] {name:20s} {size_gb:.2f} GB')
        else:
            print(f'[FAIL] {name:20s} NOT FOUND')
            found_all = False
    
    print(f'\nTotal Data Size: {total_size / 1e9:.2f} GB')
    print()
    
    if not found_all:
        print('[WARN] Some data files are missing.')
        print('Pipeline will use synthetic data instead.')
        print()
    
    return found_all


def check_directories():
    """Check/create output directories"""
    print('='*70)
    print('DIRECTORY CHECK')
    print('='*70)
    
    project_root = Path(__file__).resolve().parent.parent
    dirs_to_create = [
        str(project_root),
        str(project_root / 'data'),
        str(project_root / 'data' / 'NewYork'),
        str(project_root / 'data' / 'LosAngeles'),
        str(project_root / 'models'),
        str(project_root / 'models' / 'openvino'),
        str(project_root / 'outputs')
    ]
    
    for dir_path in dirs_to_create:
        path_obj = Path(dir_path)
        if path_obj.exists():
            print(f'[OK] {dir_path}')
        else:
            try:
                path_obj.mkdir(parents=True, exist_ok=True)
                print(f'[OK] Created {dir_path}')
            except Exception as e:
                print(f'[FAIL] Failed to create {dir_path}: {e}')
                return False
    
    print()
    return True


def check_pytorch_gpu():
    """Check GPU availability"""
    print('='*70)
    print('GPU CHECK')
    print('='*70)
    
    if torch.cuda.is_available():
        print(f'[OK] CUDA available')
        print(f'  Device: {torch.cuda.get_device_name(0)}')
        print(f'  Compute Capability: {torch.cuda.get_device_capability(0)}')
    else:
        print(f'[WARN] CUDA not available (CPU mode)')
    
    # Check MPS (Metal on Mac)
    if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        print(f'[OK] MPS (Metal) available')
    
    print()


def check_disk_space():
    """Check available disk space"""
    print('='*70)
    print('DISK SPACE CHECK')
    print('='*70)
    
    try:
        import shutil
        usage = shutil.disk_usage('C:/')
        available_gb = usage.free / 1e9
        total_gb = usage.total / 1e9
        used_pct = (usage.used / usage.total) * 100
        
        print(f'Total: {total_gb:.1f} GB')
        print(f'Used: {used_pct:.1f}%')
        print(f'Available: {available_gb:.1f} GB')
        
        if available_gb < 10:
            print(f'\n[WARN] WARNING: Low disk space (<10 GB available)')
            return False
        else:
            print(f'\n[OK] Sufficient disk space')
        
        print()
        return True
    except Exception as e:
        print(f'Could not check disk space: {e}')
        print()
        return None


def run_inference_test():
    """Quick inference test"""
    print('='*70)
    print('INFERENCE TEST')
    print('='*70)
    
    try:
        print('Creating test model...')
        # Try to import from src
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from src.phase3_training import ResMLP
        
        model = ResMLP()
        model.eval()
        
        print('Running inference...')
        with torch.no_grad():
            x = torch.randn(10, 2)
            y = model(x)
        
        print(f'[OK] Inference successful')
        print(f'  Input shape: {x.shape}')
        print(f'  Output shape: {y.shape}')
        print()
        return True
    except Exception as e:
        print(f'[FAIL] Inference test failed: {e}')
        print()
        return False


def generate_report(results):
    """Generate summary report"""
    print('='*70)
    print('DIAGNOSTIC SUMMARY')
    print('='*70)
    
    all_ok = all(results.values())
    
    if all_ok:
        print('\n[PASS] ALL CHECKS PASSED - READY TO RUN PIPELINE\n')
        print('Next steps:')
        print('1. Activate virtual environment: venv\\Scripts\\activate')
        print('2. Run pipeline: python main.py')
        print(f'3. View results in: {project_root / "outputs"}')
    else:
        print('\n[WARN] SOME CHECKS FAILED - REVIEW ABOVE\n')
        print('Common fixes:')
        print('- Install missing libraries: pip install -r requirements.txt')
        print('- Check data files are in Downloads folder')
        print('- Ensure C: drive has >10 GB free space')
    
    print()


def main():
    """Run all diagnostics"""
    print('\n')
    print('#' * 70)
    print('# SIONNA-TRANSFER: SYSTEM DIAGNOSTICS')
    print('#' * 70)
    print()
    
    results = {}
    
    # Run checks
    check_system()
    results['Libraries'] = check_libraries()
    results['Data Files'] = check_data_files()
    results['Directories'] = check_directories()
    check_pytorch_gpu()
    results['Disk Space'] = check_disk_space()
    
    # Optional tests
    try:
        sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
        results['Inference Test'] = run_inference_test()
    except Exception as e:
        print(f'Could not run inference test: {e}\n')
        results['Inference Test'] = None
    
    # Generate report
    generate_report(results)
    
    print('#' * 70)
    print()


if __name__ == '__main__':
    main()
