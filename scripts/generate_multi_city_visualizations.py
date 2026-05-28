#!/usr/bin/env python3
"""
Multi-City Comparative Analysis Visualizations
Generate 15+ plots comparing 6 cities performance
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import os

# Load results
project_root = Path(__file__).resolve().parent.parent
results_file = project_root / "multi_city_results" / "multi_city_training_results.json"
with open(results_file, 'r') as f:
    results = json.load(f)

output_dir = project_root / "multi_city_visualizations"
output_dir.mkdir(exist_ok=True)

# Configure matplotlib
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['font.size'] = 10

print("[*] Generating Multi-City Comparison Visualizations...\n")

# Extract data
cities = results['cities']
training_results = results['training_results']
transfer_results = results['transfer_results']

# City colors
city_colors = {
    'newyork': '#3498db',
    'losangeles': '#e74c3c',
    'chicago': '#2ecc71',
    'houston': '#f39c12',
    'phoenix': '#9b59b6',
    'santaclara': '#1abc9c'
}

# ============================================================================
# FIGURE 1: ACCURACY COMPARISON - ALL CITIES
# ============================================================================
print("[1/15] Accuracy Comparison Across All Cities...")
fig, ax = plt.subplots(figsize=(12, 6))

accuracies = [training_results[city]['final_accuracy'] for city in cities]
colors = [city_colors[city] for city in cities]

bars = ax.bar(range(len(cities)), accuracies, color=colors, alpha=0.7, 
              edgecolor='black', linewidth=2.5)

# Add value labels
for i, (bar, acc) in enumerate(zip(bars, accuracies)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
            f'{acc:.2f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_xticks(range(len(cities)))
ax.set_xticklabels([c.capitalize() for c in cities], rotation=45, ha='right')
ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
ax.set_title('Model Accuracy Across 6 Cities', fontsize=13, fontweight='bold')
ax.set_ylim([95, 100])
ax.grid(True, alpha=0.3, axis='y', linestyle='--')
plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig01_City_Accuracy.png', dpi=300, bbox_inches='tight')
print(f"   [OK] MC_Fig01_City_Accuracy.png")
plt.close()

# ============================================================================
# FIGURE 2: ACCURACY RANKING
# ============================================================================
print("[2/15] Accuracy Ranking (Top to Bottom)...")
fig, ax = plt.subplots(figsize=(10, 6))

ranked = sorted([(city, training_results[city]['final_accuracy']) 
                  for city in cities], key=lambda x: x[1], reverse=True)
ranked_cities = [r[0] for r in ranked]
ranked_acc = [r[1] for r in ranked]
ranked_colors = [city_colors[c] for c in ranked_cities]

bars = ax.barh(range(len(ranked_cities)), ranked_acc, color=ranked_colors, 
               alpha=0.7, edgecolor='black', linewidth=2.5)

# Add value labels
for i, (bar, acc) in enumerate(zip(bars, ranked_acc)):
    width = bar.get_width()
    ax.text(width - 0.3, bar.get_y() + bar.get_height()/2.,
            f'{acc:.2f}%', ha='right', va='center', fontsize=11, 
            fontweight='bold', color='white')

# Add rank numbers
for i in range(len(ranked_cities)):
    ax.text(-0.3, i, f'#{i+1}', ha='right', va='center', 
            fontsize=11, fontweight='bold')

ax.set_yticks(range(len(ranked_cities)))
ax.set_yticklabels([c.capitalize() for c in ranked_cities])
ax.set_xlabel('Accuracy (%)', fontsize=12, fontweight='bold')
ax.set_title('City Ranking by Model Accuracy', fontsize=13, fontweight='bold')
ax.set_xlim([96.5, 99.5])
ax.grid(True, alpha=0.3, axis='x', linestyle='--')
plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig02_City_Ranking.png', dpi=300, bbox_inches='tight')
print(f"   [OK] MC_Fig02_City_Ranking.png")
plt.close()

# ============================================================================
# FIGURE 3: TRANSFER LEARNING GAPS FROM NY
# ============================================================================
print("[3/15] Transfer Learning Gaps from New York...")
fig, ax = plt.subplots(figsize=(11, 6))

ny_transfers = [tf for tf in transfer_results if tf['source'] == 'newyork']
target_cities = [tf['target'].capitalize() for tf in ny_transfers]
gaps = [tf['transfer_gap'] for tf in ny_transfers]
zero_shot = [tf['zero_shot_acc'] for tf in ny_transfers]

x = np.arange(len(target_cities))
width = 0.35

bars1 = ax.bar(x - width/2, gaps, width, label='Transfer Gap', 
               color='#e74c3c', alpha=0.7, edgecolor='black', linewidth=2)
bars2 = ax.bar(x + width/2, zero_shot, width, label='Zero-Shot Accuracy', 
               color='#2ecc71', alpha=0.7, edgecolor='black', linewidth=2)

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.2f}%', ha='center', va='bottom', fontsize=9)

ax.set_xticks(x)
ax.set_xticklabels(target_cities)
ax.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
ax.set_title('Transfer Learning: NY Model to Other Cities', fontsize=13, fontweight='bold')
ax.legend(loc='best', framealpha=0.95)
ax.grid(True, alpha=0.3, axis='y', linestyle='--')
plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig03_NY_Transfer.png', dpi=300, bbox_inches='tight')
print(f"   [OK] MC_Fig03_NY_Transfer.png")
plt.close()

# ============================================================================
# FIGURE 4: TRANSFER LEARNING GAPS FROM LA
# ============================================================================
print("[4/15] Transfer Learning Gaps from Los Angeles...")
fig, ax = plt.subplots(figsize=(10, 6))

la_transfers = [tf for tf in transfer_results if tf['source'] == 'losangeles']
target_cities_la = [tf['target'].capitalize() for tf in la_transfers]
gaps_la = [tf['transfer_gap'] for tf in la_transfers]
zero_shot_la = [tf['zero_shot_acc'] for tf in la_transfers]

x = np.arange(len(target_cities_la))

bars1 = ax.bar(x - width/2, gaps_la, width, label='Transfer Gap', 
               color='#e74c3c', alpha=0.7, edgecolor='black', linewidth=2)
bars2 = ax.bar(x + width/2, zero_shot_la, width, label='Zero-Shot Accuracy', 
               color='#3498db', alpha=0.7, edgecolor='black', linewidth=2)

for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.2f}%', ha='center', va='bottom', fontsize=9)

ax.set_xticks(x)
ax.set_xticklabels(target_cities_la)
ax.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
ax.set_title('Transfer Learning: LA Model to Other Cities', fontsize=13, fontweight='bold')
ax.legend(loc='best', framealpha=0.95)
ax.grid(True, alpha=0.3, axis='y', linestyle='--')
plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig04_LA_Transfer.png', dpi=300, bbox_inches='tight')
print(f"   [OK] MC_Fig04_LA_Transfer.png")
plt.close()

# ============================================================================
# FIGURE 5: AVERAGE TRANSFER GAPS
# ============================================================================
print("[5/15] Average Transfer Gaps Per City...")
fig, ax = plt.subplots(figsize=(11, 6))

# Calculate average transfer gap for each target city
gap_by_target = {}
for tf in transfer_results:
    target = tf['target']
    if target not in gap_by_target:
        gap_by_target[target] = []
    gap_by_target[target].append(tf['transfer_gap'])

avg_gaps = {city: np.mean(gaps) for city, gaps in gap_by_target.items()}
sorted_cities = sorted(avg_gaps.keys(), key=lambda x: avg_gaps[x])
sorted_gaps = [avg_gaps[c] for c in sorted_cities]
colors_sorted = [city_colors[c] for c in sorted_cities]

bars = ax.bar(range(len(sorted_cities)), sorted_gaps, color=colors_sorted, 
              alpha=0.7, edgecolor='black', linewidth=2.5)

for i, (bar, gap) in enumerate(zip(bars, sorted_gaps)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
            f'{gap:.2f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax.set_xticks(range(len(sorted_cities)))
ax.set_xticklabels([c.capitalize() for c in sorted_cities], rotation=45, ha='right')
ax.set_ylabel('Average Transfer Gap (%)', fontsize=12, fontweight='bold')
ax.set_title('Average Transfer Learning Gap (Lower is Better)', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y', linestyle='--')
plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig05_Avg_Transfer_Gap.png', dpi=300, bbox_inches='tight')
print(f"   [OK] MC_Fig05_Avg_Transfer_Gap.png")
plt.close()

# ============================================================================
# FIGURE 6: TRAINING HISTORY - ALL CITIES
# ============================================================================
print("[6/15] Training Convergence History...")
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()

for idx, city in enumerate(cities):
    ax = axes[idx]
    history = training_results[city]['history']
    epochs = range(1, len(history['val_acc']) + 1)
    
    ax.plot(epochs, history['train_acc'], 'o-', color='#3498db', 
            label='Train', linewidth=2, markersize=6)
    ax.plot(epochs, history['val_acc'], 's-', color='#e74c3c', 
            label='Validation', linewidth=2, markersize=6)
    ax.fill_between(epochs, history['train_acc'], history['val_acc'], 
                    alpha=0.1, color='gray')
    
    ax.set_xlabel('Epoch', fontsize=10, fontweight='bold')
    ax.set_ylabel('Accuracy (%)', fontsize=10, fontweight='bold')
    ax.set_title(f'{city.capitalize()}', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='lower right', fontsize=9)
    ax.set_ylim([50, 100])

plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig06_Training_History.png', dpi=300, bbox_inches='tight')
print(f"   [OK] MC_Fig06_Training_History.png")
plt.close()

# ============================================================================
# FIGURE 7: TRANSFER MATRIX - ALL PAIRS
# ============================================================================
print("[7/15] Transfer Learning Matrix (Heatmap)...")
fig, ax = plt.subplots(figsize=(10, 8))

# Create matrix
n_cities = len(cities)
matrix = np.zeros((n_cities, n_cities))

for tf in transfer_results:
    src_idx = cities.index(tf['source'])
    tgt_idx = cities.index(tf['target'])
    matrix[tgt_idx, src_idx] = tf['transfer_gap']

# Diagonal is self-transfer (0)
for i in range(n_cities):
    matrix[i, i] = 0

im = ax.imshow(matrix, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=3)

# Add text annotations
for i in range(n_cities):
    for j in range(n_cities):
        text = ax.text(j, i, f'{matrix[i, j]:.2f}%',
                      ha="center", va="center", color="black", fontsize=10, fontweight='bold')

ax.set_xticks(range(n_cities))
ax.set_yticks(range(n_cities))
ax.set_xticklabels([c.capitalize() for c in cities], rotation=45, ha='right')
ax.set_yticklabels([c.capitalize() for c in cities])
ax.set_xlabel('Source City', fontsize=12, fontweight='bold')
ax.set_ylabel('Target City', fontsize=12, fontweight='bold')
ax.set_title('Transfer Learning Gap Matrix (%)', fontsize=13, fontweight='bold')

cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Transfer Gap (%)', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig07_Transfer_Matrix.png', dpi=300, bbox_inches='tight')
print(f"   [OK] MC_Fig07_Transfer_Matrix.png")
plt.close()

# ============================================================================
# FIGURE 8: CITY PAIRS - BEST & WORST TRANSFER
# ============================================================================
print("[8/15] Best and Worst Transfer Pairs...")
fig, ax = plt.subplots(figsize=(12, 6))

# Sort transfer results
sorted_transfers = sorted(transfer_results, key=lambda x: x['transfer_gap'])
best_5 = sorted_transfers[:5]
worst_5 = sorted_transfers[-5:]

all_pairs = best_5 + worst_5
pair_labels = [f"{tf['source'][:3]}->{tf['target'][:3]}" for tf in all_pairs]
gaps = [tf['transfer_gap'] for tf in all_pairs]
pair_colors = ['#2ecc71']*5 + ['#e74c3c']*5

bars = ax.barh(range(len(pair_labels)), gaps, color=pair_colors, 
               alpha=0.7, edgecolor='black', linewidth=2)

for i, (bar, gap) in enumerate(zip(bars, gaps)):
    width = bar.get_width()
    ax.text(width + 0.05, bar.get_y() + bar.get_height()/2.,
            f'{gap:.2f}%', ha='left', va='center', fontsize=9, fontweight='bold')

ax.set_yticks(range(len(pair_labels)))
ax.set_yticklabels(pair_labels)
ax.set_xlabel('Transfer Gap (%)', fontsize=12, fontweight='bold')
ax.set_title('Best and Worst Transfer Learning Pairs', fontsize=13, fontweight='bold')
ax.axvline(x=np.mean(gaps), color='gray', linestyle='--', linewidth=2, label='Average')
ax.legend()
ax.grid(True, alpha=0.3, axis='x', linestyle='--')
plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig08_Best_Worst_Pairs.png', dpi=300, bbox_inches='tight')
print(f"   [OK] MC_Fig08_Best_Worst_Pairs.png")
plt.close()

# ============================================================================
# FIGURE 9: TRAINING LOSS CONVERGENCE
# ============================================================================
print("[9/15] Training Loss Convergence...")
fig, ax = plt.subplots(figsize=(12, 6))

for city in cities:
    history = training_results[city]['history']
    epochs = range(1, len(history['train_loss']) + 1)
    ax.plot(epochs, history['train_loss'], marker='o', linewidth=2.5, 
            markersize=6, label=city.capitalize(), color=city_colors[city])

ax.set_xlabel('Epoch', fontsize=12, fontweight='bold')
ax.set_ylabel('Training Loss', fontsize=12, fontweight='bold')
ax.set_title('Training Loss Convergence Across All Cities', fontsize=13, fontweight='bold')
ax.legend(loc='best', ncol=2, framealpha=0.95)
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_xticks(range(1, 11))
plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig09_Loss_Convergence.png', dpi=300, bbox_inches='tight')
print(f"   [OK] MC_Fig09_Loss_Convergence.png")
plt.close()

# ============================================================================
# FIGURE 10: ACCURACY DISTRIBUTION
# ============================================================================
print("[10/15] Accuracy Distribution Analysis...")
fig, ax = plt.subplots(figsize=(10, 6))

accuracy_data = [training_results[city]['final_accuracy'] for city in cities]
zero_shot_data = []
for tf in transfer_results:
    zero_shot_data.append(tf['zero_shot_acc'])

parts = ax.violinplot([accuracy_data, zero_shot_data], positions=[1, 2], 
                       showmeans=True, showmedians=True, widths=0.7)

# Customize colors
colors_violin = ['#3498db', '#e74c3c']
for i, pc in enumerate(parts['bodies']):
    pc.set_facecolor(colors_violin[i])
    pc.set_alpha(0.7)

ax.set_xticks([1, 2])
ax.set_xticklabels(['Native Models', 'Zero-Shot Transfer'])
ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
ax.set_title('Accuracy Distribution: Native vs Transfer', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y', linestyle='--')
ax.set_ylim([95, 100])
plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig10_Accuracy_Distribution.png', dpi=300, bbox_inches='tight')
print(f"   [OK] MC_Fig10_Accuracy_Distribution.png")
plt.close()

# ============================================================================
# FIGURE 11: CITY SIZE vs ACCURACY
# ============================================================================
print("[11/15] Dataset Size vs Accuracy Correlation...")
fig, ax = plt.subplots(figsize=(10, 6))

# Simulate dataset sizes based on zip file sizes
dataset_sizes = {
    'newyork': 31.96,
    'losangeles': 32.19,
    'chicago': 13.92,
    'houston': 43.27,
    'phoenix': 36.09,
    'santaclara': 53.74
}

sizes = [dataset_sizes[city] for city in cities]
accs = [training_results[city]['final_accuracy'] for city in cities]
colors_list = [city_colors[city] for city in cities]

scatter = ax.scatter(sizes, accs, s=500, c=colors_list, alpha=0.7, 
                    edgecolors='black', linewidth=2)

# Add city labels
for i, city in enumerate(cities):
    ax.annotate(city.capitalize(), (sizes[i], accs[i]), 
               xytext=(5, 5), textcoords='offset points', fontsize=9)

ax.set_xlabel('Dataset Size (MB)', fontsize=12, fontweight='bold')
ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
ax.set_title('Dataset Size vs Model Accuracy', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig11_Size_vs_Accuracy.png', dpi=300, bbox_inches='tight')
print(f"   [OK] MC_Fig11_Size_vs_Accuracy.png")
plt.close()

# ============================================================================
# FIGURE 12: TRANSFER SUCCESS RATE
# ============================================================================
print("[12/15] Transfer Success Rate (>97% Accuracy)...")
fig, ax = plt.subplots(figsize=(11, 6))

# Count successful transfers (>97% accuracy)
success_by_target = {}
total_by_target = {}
for tf in transfer_results:
    target = tf['target']
    if target not in success_by_target:
        success_by_target[target] = 0
        total_by_target[target] = 0
    total_by_target[target] += 1
    if tf['zero_shot_acc'] > 97:
        success_by_target[target] += 1

success_rate = {city: (success_by_target.get(city, 0) / total_by_target.get(city, 1)) * 100 
                for city in cities}
sorted_cities_sr = sorted(success_rate.keys(), key=lambda x: success_rate[x], reverse=True)
sorted_rates = [success_rate[c] for c in sorted_cities_sr]
colors_sr = [city_colors[c] for c in sorted_cities_sr]

bars = ax.bar(range(len(sorted_cities_sr)), sorted_rates, color=colors_sr, 
              alpha=0.7, edgecolor='black', linewidth=2.5)

for i, (bar, rate) in enumerate(zip(bars, sorted_rates)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 2,
            f'{rate:.0f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_xticks(range(len(sorted_cities_sr)))
ax.set_xticklabels([c.capitalize() for c in sorted_cities_sr], rotation=45, ha='right')
ax.set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
ax.set_title('Transfer Success Rate (>97% Accuracy Threshold)', fontsize=13, fontweight='bold')
ax.set_ylim([0, 110])
ax.grid(True, alpha=0.3, axis='y', linestyle='--')
plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig12_Success_Rate.png', dpi=300, bbox_inches='tight')
print(f"   [OK] MC_Fig12_Success_Rate.png")
plt.close()

# ============================================================================
# FIGURE 13: SUMMARY STATISTICS TABLE
# ============================================================================
print("[13/15] Summary Statistics...")
fig, ax = plt.subplots(figsize=(14, 6))
ax.axis('tight')
ax.axis('off')

table_data = []
table_data.append(['City', 'Accuracy', 'Best Transfer', 'Worst Transfer', 'Avg Gap'])

for city in sorted(cities, key=lambda x: training_results[x]['final_accuracy'], reverse=True):
    acc = training_results[city]['final_accuracy']
    
    # Find best and worst transfer
    city_transfers = [tf for tf in transfer_results if tf['target'] == city]
    if city_transfers:
        best = min(city_transfers, key=lambda x: x['transfer_gap'])
        worst = max(city_transfers, key=lambda x: x['transfer_gap'])
        avg_gap = np.mean([tf['transfer_gap'] for tf in city_transfers])
        best_str = f"{best['source'][:3]} ({best['zero_shot_acc']:.2f}%)"
        worst_str = f"{worst['source'][:3]} ({worst['zero_shot_acc']:.2f}%)"
    else:
        best_str = "N/A"
        worst_str = "N/A"
        avg_gap = 0
    
    table_data.append([
        city.capitalize(),
        f"{acc:.2f}%",
        best_str,
        worst_str,
        f"{avg_gap:.2f}%"
    ])

table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                colWidths=[0.15, 0.15, 0.25, 0.25, 0.15])
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2.5)

# Style header
for i in range(5):
    table[(0, i)].set_facecolor('#3498db')
    table[(0, i)].set_text_props(weight='bold', color='white')

# Alternate row colors
for i in range(1, len(table_data)):
    for j in range(5):
        if i % 2 == 0:
            table[(i, j)].set_facecolor('#ecf0f1')
        else:
            table[(i, j)].set_facecolor('white')

plt.title('Multi-City Training Summary', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig13_Summary_Table.png', dpi=300, bbox_inches='tight')
print(f"   [OK] MC_Fig13_Summary_Table.png")
plt.close()

# ============================================================================
# FIGURE 14: EPOCH PROGRESSION - BEST CITY
# ============================================================================
print("[14/15] Epoch Progression (Best City)...")
best_city = max(cities, key=lambda x: training_results[x]['final_accuracy'])
fig, ax = plt.subplots(figsize=(12, 6))

history = training_results[best_city]['history']
epochs = range(1, len(history['val_acc']) + 1)

ax.fill_between(epochs, history['train_acc'], history['val_acc'], 
               alpha=0.2, color='gray', label='Train-Val Gap')
ax.plot(epochs, history['train_acc'], 'o-', color='#3498db', linewidth=2.5, 
       markersize=8, label='Training Accuracy')
ax.plot(epochs, history['val_acc'], 's-', color='#e74c3c', linewidth=2.5, 
       markersize=8, label='Validation Accuracy')

ax.set_xlabel('Epoch', fontsize=12, fontweight='bold')
ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
ax.set_title(f'Best Performing City: {best_city.capitalize()} ({training_results[best_city]["final_accuracy"]:.2f}%)', 
            fontsize=13, fontweight='bold')
ax.legend(loc='lower right', fontsize=11, framealpha=0.95)
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_xticks(epochs)
plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig14_Best_City_Progression.png', dpi=300, bbox_inches='tight')
print(f"   [OK] MC_Fig14_Best_City_Progression.png")
plt.close()

# ============================================================================
# FIGURE 15: PERFORMANCE RANGE & VARIABILITY
# ============================================================================
print("[15/15] Performance Range & Variability...")
fig, ax = plt.subplots(figsize=(12, 6))

accuracies_native = [training_results[city]['final_accuracy'] for city in cities]
accuracies_transfer = [tf['zero_shot_acc'] for tf in transfer_results]

# Box plot
bp = ax.boxplot([accuracies_native, accuracies_transfer], labels=['Native Models', 'Zero-Shot Transfer'],
                patch_artist=True, widths=0.5, showfliers=True)

# Customize colors
colors_box = ['#3498db', '#e74c3c']
for patch, color in zip(bp['boxes'], colors_box):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

# Style whiskers, caps, medians
for whisker in bp['whiskers']:
    whisker.set(linewidth=2, color='black')
for cap in bp['caps']:
    cap.set(linewidth=2, color='black')
for median in bp['medians']:
    median.set(linewidth=2.5, color='darkred')

ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
ax.set_title('Accuracy Distribution: Range and Variability', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y', linestyle='--')
ax.set_ylim([95, 100])

# Add statistics
native_mean = np.mean(accuracies_native)
transfer_mean = np.mean(accuracies_transfer)
ax.text(1, 95.5, f'Mean: {native_mean:.2f}%', ha='center', fontsize=10, fontweight='bold')
ax.text(2, 95.5, f'Mean: {transfer_mean:.2f}%', ha='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig15_Performance_Range.png', dpi=300, bbox_inches='tight')
print(f"   [OK] MC_Fig15_Performance_Range.png")
plt.close()

# ============================================================================
# Print Summary
# ============================================================================
print("\n" + "="*70)
print("MULTI-CITY VISUALIZATIONS COMPLETE!")
print("="*70)
print(f"Output Directory: {output_dir}/")
print(f"Total Figures Generated: 15")
print("\nGenerated Figures:")
for i in range(1, 16):
    print(f"  {i:2d}. MC_Fig{i:02d}_*.png")

print("\n" + "="*70)
