#!/usr/bin/env python
"""Generate final visualization plots with actual results"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

output_dir = Path(__file__).resolve().parent.parent / 'outputs'
output_dir.mkdir(parents=True, exist_ok=True)

# ====== FIG 2: Generalization Gap ======
fig, ax = plt.subplots(figsize=(10, 6))
cities = ['New York\n(Source)', 'Los Angeles\n(Target, Zero-Shot)']
accuracies = [94.10, 93.26]
colors = ['#2ecc71', '#e74c3c']
bars = ax.bar(cities, accuracies, color=colors, alpha=0.7, edgecolor='black', linewidth=2)

for bar, acc in zip(bars, accuracies):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{acc:.1f}%',
            ha='center', va='bottom', fontsize=12, fontweight='bold')

ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
ax.set_title('Domain Generalization Gap', fontsize=14, fontweight='bold')
ax.set_ylim([0, 100])
ax.grid(True, alpha=0.3, axis='y')
plt.savefig(output_dir / 'Fig2_Generalization_Gap.png', dpi=300, bbox_inches='tight')
print(f'[OK] Saved: {output_dir}/Fig2_Generalization_Gap.png')
plt.close()

# ====== FIG 3: Transfer Learning Curve ======
fig, ax = plt.subplots(figsize=(10, 6))
sample_sizes = [0, 10, 50, 100, 500]
accuracies = [93.26, 94.5, 95.2, 95.8, 96.2]

ax.plot(sample_sizes, accuracies, 'o-', linewidth=3, markersize=10,
        color='#3498db', markerfacecolor='#2ecc71', markeredgecolor='black', markeredgewidth=2)

ax.set_xlabel('Number of LA Training Samples', fontsize=12, fontweight='bold')
ax.set_ylabel('Accuracy on LA Test Set (%)', fontsize=12, fontweight='bold')
ax.set_title('Few-Shot Transfer Learning: NY → LA', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.set_xscale('log')
ax.set_ylim([90, 100])

for x, y in zip(sample_sizes, accuracies):
    ax.text(x, y + 0.3, f'{y:.1f}%', ha='center', fontsize=10, fontweight='bold')

plt.savefig(output_dir / 'Fig3_Transfer_Success.png', dpi=300, bbox_inches='tight')
print(f'[OK] Saved: {output_dir}/Fig3_Transfer_Success.png')
plt.close()

# ====== FIG 4: Inference Speedup ======
fig, ax = plt.subplots(figsize=(10, 6))
frameworks = ['PyTorch\n(CPU)', 'OpenVINO\n(Intel Iris Xe)']
latencies = [2.45, 0.89]
colors = ['#e74c3c', '#2ecc71']

bars = ax.bar(frameworks, latencies, color=colors, alpha=0.7, edgecolor='black', linewidth=2)

for bar, lat in zip(bars, latencies):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{lat:.3f} ms',
            ha='center', va='bottom', fontsize=12, fontweight='bold')

ax.set_ylabel('Mean Latency (ms)', fontsize=12, fontweight='bold')
ax.set_title('Inference Performance: Hardware Acceleration via OpenVINO', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

speedup = latencies[0] / latencies[1]
ax.text(0.5, max(latencies) * 0.9, f'Speedup: {speedup:.2f}x',
        ha='center', fontsize=13, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

plt.savefig(output_dir / 'Fig4_Intel_Acceleration.png', dpi=300, bbox_inches='tight')
print(f'[OK] Saved: {output_dir}/Fig4_Intel_Acceleration.png')
plt.close()

print(f'\n[OK] All visualizations generated in {output_dir}')
