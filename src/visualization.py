"""
Visualization Module
Generate all 4 required plots
"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def plot_city_coverage_map(dataset, predictions, city_name='New York', save_path=None):
    """
    Fig 1: 2D Scatter plot of user locations colored by best beam
    
    Args:
        dataset: Dict with 'positions_original' tensor
        predictions: Array of predicted beam indices
        city_name: Name of city
        save_path: Where to save figure
    """
    positions = dataset['positions_original'].numpy()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    scatter = ax.scatter(
        positions[:, 0],
        positions[:, 1],
        c=predictions,
        cmap='tab20b',
        s=20,
        alpha=0.6,
        edgecolors='k',
        linewidth=0.3
    )
    
    ax.set_xlabel('X Position (meters)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Y Position (meters)', fontsize=12, fontweight='bold')
    ax.set_title(f'Beam Coverage Map - {city_name}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Beam Index', fontsize=11, fontweight='bold')
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f'[OK] Saved: {save_path}')
    
    return fig


def plot_generalization_gap(ny_acc, la_zero_shot_acc, save_path=None):
    """
    Fig 2: Bar chart showing NY vs LA accuracy (generalization gap)
    
    Args:
        ny_acc: Accuracy on NY test set
        la_zero_shot_acc: Zero-shot accuracy on LA data
        save_path: Where to save figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    cities = ['New York\n(Source)', 'Los Angeles\n(Target, Zero-Shot)']
    accuracies = [ny_acc, la_zero_shot_acc]
    colors = ['#2ecc71', '#e74c3c']
    
    bars = ax.bar(cities, accuracies, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    
    # Add value labels on bars
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{acc:.1f}%',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_title('Domain Generalization Gap', fontsize=14, fontweight='bold')
    ax.set_ylim([0, 100])
    ax.grid(True, alpha=0.3, axis='y')
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f'✓ Saved: {save_path}')
    
    return fig


def plot_transfer_learning_curve(few_shot_results, save_path=None):
    """
    Fig 3: Line plot of accuracy vs number of training samples
    
    Args:
        few_shot_results: Dict mapping num_samples -> accuracy
        save_path: Where to save figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    sample_sizes = sorted(few_shot_results.keys())
    accuracies = [few_shot_results[n] for n in sample_sizes]
    
    ax.plot(sample_sizes, accuracies, 'o-', linewidth=3, markersize=10,
            color='#3498db', markerfacecolor='#2ecc71', markeredgecolor='black', markeredgewidth=2)
    
    ax.set_xlabel('Number of LA Training Samples', fontsize=12, fontweight='bold')
    ax.set_ylabel('Accuracy on LA Test Set (%)', fontsize=12, fontweight='bold')
    ax.set_title('Few-Shot Transfer Learning: NY → LA', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log')
    ax.set_ylim([0, 100])
    
    # Add value labels
    for x, y in zip(sample_sizes, accuracies):
        ax.text(x, y + 2, f'{y:.1f}%', ha='center', fontsize=10, fontweight='bold')
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f'✓ Saved: {save_path}')
    
    return fig


def plot_inference_speedup(pytorch_latency, openvino_latency, save_path=None):
    """
    Fig 4: Bar chart comparing inference latency
    
    Args:
        pytorch_latency: Mean latency for PyTorch (ms)
        openvino_latency: Mean latency for OpenVINO (ms)
        save_path: Where to save figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    frameworks = ['PyTorch\n(CPU)', 'OpenVINO\n(Intel Iris Xe)']
    latencies = [pytorch_latency, openvino_latency]
    colors = ['#e74c3c', '#2ecc71']
    
    bars = ax.bar(frameworks, latencies, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    
    # Add value labels
    for bar, lat in zip(bars, latencies):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{lat:.3f} ms',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    ax.set_ylabel('Mean Latency (ms)', fontsize=12, fontweight='bold')
    ax.set_title('Inference Performance: Hardware Acceleration via OpenVINO', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add speedup annotation
    if openvino_latency > 0:
        speedup = pytorch_latency / openvino_latency
        ax.text(0.5, max(latencies) * 0.9, f'Speedup: {speedup:.2f}x',
                ha='center', fontsize=13, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f'✓ Saved: {save_path}')
    
    return fig


def generate_summary_report(results_dict, output_dir=None):
    """
    Generate comprehensive summary report with all figures
    
    Args:
        results_dict: Dict containing all metrics and data
        output_dir: Where to save figures
    """
    if output_dir is None:
        project_root = Path(__file__).resolve().parent.parent
        output_dir = str(project_root / 'outputs')
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print('\n' + '='*60)
    print('GENERATING VISUALIZATION REPORT')
    print('='*60)
    
    # Fig 1: Coverage Map
    if 'ny_dataset' in results_dict:
        plot_city_coverage_map(
            results_dict['ny_dataset'],
            results_dict.get('ny_predictions', np.zeros(100)),
            city_name='New York',
            save_path=f'{output_dir}/Fig1_NY_Coverage_Map.png'
        )
    
    # Fig 2: Generalization Gap
    if 'ny_accuracy' in results_dict and 'la_zero_shot_accuracy' in results_dict:
        plot_generalization_gap(
            results_dict['ny_accuracy'],
            results_dict['la_zero_shot_accuracy'],
            save_path=f'{output_dir}/Fig2_Generalization_Gap.png'
        )
    
    # Fig 3: Transfer Learning Curve
    if 'few_shot_results' in results_dict:
        plot_transfer_learning_curve(
            results_dict['few_shot_results'],
            save_path=f'{output_dir}/Fig3_Transfer_Success.png'
        )
    
    # Fig 4: Inference Speedup
    if 'pytorch_latency' in results_dict and 'openvino_latency' in results_dict:
        plot_inference_speedup(
            results_dict['pytorch_latency'],
            results_dict['openvino_latency'],
            save_path=f'{output_dir}/Fig4_Intel_Acceleration.png'
        )
    
    print(f'\n[OK] All figures saved to {output_dir}')


if __name__ == '__main__':
    print('Visualization Module')
    print('-' * 50)
    
    # Example usage with synthetic data
    example_data = {
        'ny_accuracy': 78.5,
        'la_zero_shot_accuracy': 42.3,
        'few_shot_results': {0: 42.3, 10: 55.8, 50: 68.9, 100: 75.2, 500: 82.1},
        'pytorch_latency': 2.45,
        'openvino_latency': 0.89
    }
    
    generate_summary_report(example_data)
