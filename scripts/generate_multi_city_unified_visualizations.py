#!/usr/bin/env python3
"""
Enhanced Multi-City Unified Visualizations
All 15 plots now include ALL CITY DATA in each image for easy visual comparison
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Load results
project_root = Path(__file__).resolve().parent.parent
results_file = project_root / "multi_city_results" / "multi_city_training_results.json"
with open(results_file, 'r') as f:
    results = json.load(f)

output_dir = project_root / "multi_city_visualizations"
output_dir.mkdir(exist_ok=True)

# Configure matplotlib for high-quality output
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'sans-serif'

print("[*] Generating Enhanced Multi-City Unified Visualizations (All Cities in Each Image)...\n")

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

city_display_names = {
    'newyork': 'New York',
    'losangeles': 'Los Angeles',
    'chicago': 'Chicago',
    'houston': 'Houston',
    'phoenix': 'Phoenix',
    'santaclara': 'Santa Clara'
}

# ============================================================================
# FIGURE 1: ACCURACY COMPARISON - ALL CITIES
# ============================================================================
print("[1/15] Accuracy Comparison - All Cities in Single View...")
fig, ax = plt.subplots(figsize=(14, 7))

accuracies = [training_results[city]['final_accuracy'] for city in cities]
colors = [city_colors[city] for city in cities]
display_names = [city_display_names[city] for city in cities]

bars = ax.bar(range(len(cities)), accuracies, color=colors, alpha=0.8, 
              edgecolor='black', linewidth=2.5, width=0.6)

for i, (bar, acc) in enumerate(zip(bars, accuracies)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.08,
            f'{acc:.2f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')

ax.set_xticks(range(len(cities)))
ax.set_xticklabels(display_names, rotation=45, ha='right', fontsize=11)
ax.set_ylabel('Accuracy (%)', fontsize=13, fontweight='bold')
ax.set_title('Model Accuracy Across All 6 Cities\n(All city data in single comparison)', 
             fontsize=14, fontweight='bold', pad=20)
ax.set_ylim([96.5, 99.5])
ax.grid(True, alpha=0.3, axis='y', linestyle='--')
ax.axhline(y=np.mean(accuracies), color='red', linestyle='--', linewidth=2, 
           label=f'Average: {np.mean(accuracies):.2f}%', alpha=0.7)
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig01_City_Accuracy_ALL.png', dpi=300, bbox_inches='tight')
print(f"   ✓ MC_Fig01_City_Accuracy_ALL.png - All 6 cities visible")
plt.close()

# ============================================================================
# FIGURE 2: ACCURACY RANKING WITH ALL CITIES
# ============================================================================
print("[2/15] Accuracy Ranking - All Cities Ranked...")
fig, ax = plt.subplots(figsize=(14, 8))

ranked = sorted([(city, training_results[city]['final_accuracy']) 
                  for city in cities], key=lambda x: x[1], reverse=True)
ranked_cities = [r[0] for r in ranked]
ranked_acc = [r[1] for r in ranked]
ranked_colors = [city_colors[c] for c in ranked_cities]
ranked_display = [city_display_names[c] for c in ranked_cities]

bars = ax.barh(range(len(ranked_cities)), ranked_acc, color=ranked_colors, 
               alpha=0.8, edgecolor='black', linewidth=2.5, height=0.6)

for i, (bar, acc) in enumerate(zip(bars, ranked_acc)):
    width = bar.get_width()
    ax.text(width - 0.2, bar.get_y() + bar.get_height()/2.,
            f'{acc:.2f}%', ha='right', va='center', fontsize=12, 
            fontweight='bold', color='white')

for i in range(len(ranked_cities)):
    badge = f'#{i+1}'
    ax.text(96.7, i, badge, ha='left', va='center', 
            fontsize=11, fontweight='bold')

ax.set_yticks(range(len(ranked_cities)))
ax.set_yticklabels(ranked_display, fontsize=11)
ax.set_xlabel('Accuracy (%)', fontsize=13, fontweight='bold')
ax.set_title('City Accuracy Rankings\n(All 6 cities ranked by performance)', 
             fontsize=14, fontweight='bold', pad=20)
ax.set_xlim([96.5, 99.5])
ax.grid(True, alpha=0.3, axis='x', linestyle='--')
plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig02_City_Ranking_ALL.png', dpi=300, bbox_inches='tight')
print(f"   ✓ MC_Fig02_City_Ranking_ALL.png - All 6 cities ranked")
plt.close()

# ============================================================================
# FIGURE 3: TRANSFER LEARNING MATRIX - ALL CITIES
# ============================================================================
print("[3/15] Transfer Learning Matrix - All Source/Target Combinations...")
fig, ax = plt.subplots(figsize=(14, 10))

transfer_matrix = np.zeros((len(cities), len(cities)))
for i, source_city in enumerate(cities):
    for j, target_city in enumerate(cities):
        if i == j:
            transfer_matrix[j, i] = training_results[source_city]['final_accuracy']
        else:
            for transfer in transfer_results:
                if transfer['source'] == source_city and transfer['target'] == target_city:
                    transfer_matrix[j, i] = transfer['zero_shot_acc']

im = ax.imshow(transfer_matrix, cmap='RdYlGn', aspect='auto', vmin=95, vmax=100)

ax.set_xticks(range(len(cities)))
ax.set_yticks(range(len(cities)))
ax.set_xticklabels([city_display_names[c] for c in cities], rotation=45, ha='right', fontsize=11)
ax.set_yticklabels([city_display_names[c] for c in cities], fontsize=11)
ax.set_xlabel('Source City (Model Trained)', fontsize=13, fontweight='bold')
ax.set_ylabel('Target City (Model Deployed)', fontsize=13, fontweight='bold')
ax.set_title('Transfer Learning Performance Matrix\n(All 36 source→target combinations shown)', 
             fontsize=14, fontweight='bold', pad=20)

for i in range(len(cities)):
    for j in range(len(cities)):
        text = ax.text(j, i, f'{transfer_matrix[i, j]:.2f}%',
                      ha="center", va="center", color="black", fontsize=9, fontweight='bold')

cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label('Accuracy (%)', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig03_Transfer_Matrix_ALL.png', dpi=300, bbox_inches='tight')
print(f"   ✓ MC_Fig03_Transfer_Matrix_ALL.png - All 36 combinations visible")
plt.close()

# ============================================================================
# FIGURE 4: TRANSFER SUCCESS ANALYSIS - ALL CITIES
# ============================================================================
print("[4/15] Transfer Success Rate - All City Pairs...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

source_success = {}
for source_city in cities:
    transfers = [t for t in transfer_results if t['source'] == source_city]
    if transfers:
        success = sum(1 for t in transfers if t['zero_shot_acc'] >= 97.0)
        source_success[source_city] = (success, len(transfers))

sources = list(source_success.keys())
success_counts = [source_success[s][0] for s in sources]
total_counts = [source_success[s][1] for s in sources]
colors_list = [city_colors[c] for c in sources]
display_names_list = [city_display_names[c] for c in sources]

bars1 = ax1.bar(range(len(sources)), success_counts, color=colors_list, alpha=0.8,
                edgecolor='black', linewidth=2.5, width=0.6)

for i, (bar, count, total) in enumerate(zip(bars1, success_counts, total_counts)):
    if total > 0:
        height = bar.get_height()
        percentage = (count / total) * 100
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{count}/{total}\n({percentage:.0f}%)', ha='center', va='bottom', 
                fontsize=10, fontweight='bold')

ax1.set_xticks(range(len(sources)))
ax1.set_xticklabels(display_names_list, rotation=45, ha='right', fontsize=11)
ax1.set_ylabel('Successful Transfers (≥97%)', fontsize=12, fontweight='bold')
ax1.set_title('Transfer Success by Source City\n(All 6 cities as sources)', 
              fontsize=13, fontweight='bold')
ax1.set_ylim([0, 6])
ax1.grid(True, alpha=0.3, axis='y', linestyle='--')

gaps = []
pair_labels = []
gap_colors = []

for transfer in transfer_results:
    source_acc = training_results[transfer['source']]['final_accuracy']
    target_acc = transfer['zero_shot_acc']
    gap = source_acc - target_acc
    gaps.append(gap)
    source_disp = city_display_names[transfer['source']][:3]
    target_disp = city_display_names[transfer['target']][:3]
    pair_labels.append(f'{source_disp}→{target_disp}')
    gap_colors.append(city_colors[transfer['source']])

sorted_indices = np.argsort(gaps)
sorted_gaps = [gaps[i] for i in sorted_indices]
sorted_labels = [pair_labels[i] for i in sorted_indices]
sorted_colors = [gap_colors[i] for i in sorted_indices]

bars2 = ax2.barh(range(len(sorted_gaps)), sorted_gaps, color=sorted_colors, alpha=0.8,
                 edgecolor='black', linewidth=1.5, height=0.7)

ax2.set_yticks(range(len(sorted_labels)))
ax2.set_yticklabels(sorted_labels, fontsize=8)
ax2.set_xlabel('Transfer Gap (%)', fontsize=12, fontweight='bold')
ax2.set_title('All 10 Transfer Gaps (Sorted)\n(All source→target transfers shown)', 
              fontsize=13, fontweight='bold')
ax2.axvline(x=np.mean(sorted_gaps), color='red', linestyle='--', linewidth=2, 
            label=f'Average Gap: {np.mean(sorted_gaps):.2f}%', alpha=0.7)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3, axis='x', linestyle='--')

plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig04_Transfer_Success_ALL.png', dpi=300, bbox_inches='tight')
print(f"   ✓ MC_Fig04_Transfer_Success_ALL.png - All transfers analyzed")
plt.close()

# ============================================================================
# FIGURE 5: PERFORMANCE DISTRIBUTION - ALL RESULTS
# ============================================================================
print("[5/15] Performance Distribution - All City Results...")
fig, ax = plt.subplots(figsize=(14, 8))

all_accs = []
all_labels = []
all_colors = []

for city in cities:
    acc = training_results[city]['final_accuracy']
    all_accs.append(acc)
    all_labels.append(f'{city_display_names[city]}\n(Native)')
    all_colors.append(city_colors[city])
    
    transfers_to = [t for t in transfer_results if t['target'] == city]
    for transfer in transfers_to:
        all_accs.append(transfer['zero_shot_acc'])
        source_short = city_display_names[transfer['source']][:3]
        all_labels.append(f'{source_short}→\n{city_display_names[city][:3]}')
        all_colors.append(city_colors[transfer['source']])

y_pos = np.arange(len(all_accs))
bars = ax.barh(y_pos, all_accs, color=all_colors, alpha=0.8, 
               edgecolor='black', linewidth=1.2, height=0.7)

for i, (acc, bar) in enumerate(zip(all_accs, bars)):
    ax.text(acc - 0.4, bar.get_y() + bar.get_height()/2.,
            f'{acc:.2f}%', ha='right', va='center', fontsize=8, 
            fontweight='bold', color='white')

ax.set_yticks(y_pos)
ax.set_yticklabels(all_labels, fontsize=8)
ax.set_xlabel('Accuracy (%)', fontsize=13, fontweight='bold')
ax.set_title('All Performance Results - 6 Cities + 10 Transfers\n(Complete accuracy overview)', 
             fontsize=14, fontweight='bold', pad=20)
ax.set_xlim([95.5, 99.5])
ax.axvline(x=97.0, color='green', linestyle='--', linewidth=2, label='Target: 97%', alpha=0.5)
ax.grid(True, alpha=0.3, axis='x', linestyle='--')
ax.legend(fontsize=11)

plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig05_Performance_Distribution_ALL.png', dpi=300, bbox_inches='tight')
print(f"   ✓ MC_Fig05_Performance_Distribution_ALL.png - 16 results shown")
plt.close()

# ============================================================================
# FIGURE 6: LOSS CONVERGENCE - ALL CITIES
# ============================================================================
print("[6/15] Training Loss Convergence - All Cities...")
fig, ax = plt.subplots(figsize=(14, 8))

for city in cities:
    history = training_results[city]['history']
    train_loss = history['train_loss']
    epochs = range(1, len(train_loss) + 1)
    ax.plot(epochs, train_loss, marker='o', linewidth=2.5, markersize=6,
            label=city_display_names[city], color=city_colors[city], alpha=0.8)

ax.set_xlabel('Epoch', fontsize=13, fontweight='bold')
ax.set_ylabel('Loss (BCEWithLogitsLoss)', fontsize=13, fontweight='bold')
ax.set_title('Training Loss Convergence - All 6 Cities\n(Loss curves overlaid for comparison)', 
             fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, linestyle='--')
ax.legend(loc='upper right', fontsize=11, framealpha=0.95)

plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig06_Loss_Convergence_ALL.png', dpi=300, bbox_inches='tight')
print(f"   ✓ MC_Fig06_Loss_Convergence_ALL.png - All cities' loss curves")
plt.close()

# ============================================================================
# FIGURE 7: ACCURACY VS TRANSFER GAP - ALL CITIES
# ============================================================================
print("[7/15] Accuracy vs Transfer Gap - All Cities Analyzed...")
fig, ax = plt.subplots(figsize=(14, 8))

city_data = []
for source_city in cities:
    source_acc = training_results[source_city]['final_accuracy']
    transfers_from = [t for t in transfer_results if t['source'] == source_city]
    avg_gap = np.mean([training_results[source_city]['final_accuracy'] - t['zero_shot_acc'] 
                       for t in transfers_from])
    city_data.append((source_city, source_acc, avg_gap))

source_cities = [c[0] for c in city_data]
source_accs = [c[1] for c in city_data]
avg_gaps = [c[2] for c in city_data]
colors_list = [city_colors[c] for c in source_cities]
display_names_list = [city_display_names[c] for c in source_cities]

scatter = ax.scatter(source_accs, avg_gaps, s=400, c=colors_list, alpha=0.8,
                     edgecolor='black', linewidth=2.5, zorder=3)

for i, (city_disp, acc, gap) in enumerate(zip(display_names_list, source_accs, avg_gaps)):
    ax.annotate(city_disp, (acc, gap), textcoords="offset points", 
                xytext=(0, 10), ha='center', fontsize=10, fontweight='bold')

ax.set_xlabel('City Training Accuracy (%)', fontsize=13, fontweight='bold')
ax.set_ylabel('Average Transfer Gap (%)', fontsize=13, fontweight='bold')
ax.set_title('Accuracy vs Transfer Gap - All 6 Cities as Source\n(Better models show different transfer characteristics)', 
             fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, linestyle='--')

z = np.polyfit(source_accs, avg_gaps, 1)
p = np.poly1d(z)
x_trend = np.linspace(min(source_accs), max(source_accs), 100)
ax.plot(x_trend, p(x_trend), "r--", linewidth=2, alpha=0.5, label='Trend line')
ax.legend(fontsize=11)

plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig07_Accuracy_vs_Gap_ALL.png', dpi=300, bbox_inches='tight')
print(f"   ✓ MC_Fig07_Accuracy_vs_Gap_ALL.png - All 6 cities plotted")
plt.close()

# ============================================================================
# FIGURE 8: ACCURACY IMPROVEMENT OVER EPOCHS - ALL CITIES
# ============================================================================
print("[8/15] Accuracy Improvement Over Epochs - All Cities...")
fig, ax = plt.subplots(figsize=(14, 8))

for city in cities:
    history = training_results[city]['history']
    val_acc = history['val_acc']
    epochs = range(1, len(val_acc) + 1)
    ax.plot(epochs, val_acc, marker='s', linewidth=2.5, markersize=6,
            label=city_display_names[city], color=city_colors[city], alpha=0.8)

ax.set_xlabel('Epoch', fontsize=13, fontweight='bold')
ax.set_ylabel('Validation Accuracy (%)', fontsize=13, fontweight='bold')
ax.set_title('Accuracy Improvement Over Epochs - All 6 Cities\n(Convergence curves overlaid for comparison)', 
             fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, linestyle='--')
ax.legend(loc='lower right', fontsize=11, framealpha=0.95)
ax.set_ylim([60, 100])

plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig08_Accuracy_Curves_ALL.png', dpi=300, bbox_inches='tight')
print(f"   ✓ MC_Fig08_Accuracy_Curves_ALL.png - All cities convergence")
plt.close()

# ============================================================================
# FIGURE 9: SUMMARY TABLE - ALL CITIES & METRICS
# ============================================================================
print("[9/15] Summary Table - All Cities Complete Metrics...")
fig, ax = plt.subplots(figsize=(16, 8))
ax.axis('tight')
ax.axis('off')

table_data = []
headers = ['City', 'Accuracy (%)', 'Epochs', 'Final Loss', 'Avg Transfer Gap (%)', 'Status']

for city in cities:
    acc = training_results[city]['final_accuracy']
    epochs = training_results[city]['epochs']
    final_loss = training_results[city]['history']['train_loss'][-1]
    
    transfers_from = [t for t in transfer_results if t['source'] == city]
    avg_gap = np.mean([training_results[city]['final_accuracy'] - t['zero_shot_acc'] 
                       for t in transfers_from])
    
    status = "Excellent" if acc >= 98.5 else "Good" if acc >= 98 else "Pass"
    
    table_data.append([
        city_display_names[city],
        f'{acc:.2f}%',
        f'{int(epochs)}',
        f'{final_loss:.4f}',
        f'{avg_gap:.2f}%',
        status
    ])

table = ax.table(cellText=table_data, colLabels=headers, cellLoc='center', 
                loc='center', colWidths=[0.15, 0.15, 0.15, 0.15, 0.15, 0.15])

table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1, 2.5)

for i in range(len(headers)):
    table[(0, i)].set_facecolor('#3498db')
    table[(0, i)].set_text_props(weight='bold', color='white')

for i in range(1, len(table_data) + 1):
    for j in range(len(headers)):
        if i % 2 == 0:
            table[(i, j)].set_facecolor('#ecf0f1')
        else:
            table[(i, j)].set_facecolor('#f8f9fa')
        table[(i, j)].set_text_props(weight='bold')

plt.title('Complete Summary Table - All 6 Cities\n(All metrics unified in single view)', 
          fontsize=14, fontweight='bold', pad=20)
plt.savefig(output_dir / 'MC_Fig09_Summary_Table_ALL.png', dpi=300, bbox_inches='tight')
print(f"   ✓ MC_Fig09_Summary_Table_ALL.png - Complete metrics table")
plt.close()

# ============================================================================
# FIGURE 10: PERFORMANCE HEATMAP - TRAINING + TRANSFER
# ============================================================================
print("[10/15] Performance Heatmap - Training & Transfer Results...")
fig, ax = plt.subplots(figsize=(14, 10))

combined_matrix = np.zeros((len(cities), len(cities)))

for i, target_city in enumerate(cities):
    for j, source_city in enumerate(cities):
        if i == j:
            combined_matrix[i, j] = training_results[target_city]['final_accuracy']
        else:
            for transfer in transfer_results:
                if transfer['source'] == source_city and transfer['target'] == target_city:
                    combined_matrix[i, j] = transfer['zero_shot_acc']

im = ax.imshow(combined_matrix, cmap='RdYlGn', aspect='auto', vmin=96, vmax=99.5)

display_names_short = [city_display_names[c][:3] for c in cities]
ax.set_xticks(range(len(cities)))
ax.set_yticks(range(len(cities)))
ax.set_xticklabels(display_names_short, fontsize=11)
ax.set_yticklabels(display_names_short, fontsize=11)
ax.set_xlabel('Source City Model', fontsize=13, fontweight='bold')
ax.set_ylabel('Target City Deployment', fontsize=13, fontweight='bold')
ax.set_title('Complete Performance Heatmap - All Cities\n(Diagonal: training, Off-diagonal: transfer learning)', 
             fontsize=14, fontweight='bold', pad=20)

for i in range(len(cities)):
    for j in range(len(cities)):
        text = ax.text(j, i, f'{combined_matrix[i, j]:.2f}%',
                      ha="center", va="center", color="black", fontsize=9, fontweight='bold')

cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label('Accuracy (%)', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig10_Performance_Heatmap_ALL.png', dpi=300, bbox_inches='tight')
print(f"   ✓ MC_Fig10_Performance_Heatmap_ALL.png - All 36 results")
plt.close()

# ============================================================================
# FIGURE 11: DEPLOYMENT SCENARIOS - ALL CITIES
# ============================================================================
print("[11/15] Deployment Scenarios - All Cities Compared...")
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

ny_transfers = [t for t in transfer_results if t['source'] == 'newyork']
ny_target_cities = [t['target'] for t in ny_transfers]
ny_accuracies = [t['zero_shot_acc'] for t in ny_transfers]
ny_colors = [city_colors[c] for c in ny_target_cities]
ny_display = [city_display_names[c] for c in ny_target_cities]

bars1 = ax1.bar(range(len(ny_display)), ny_accuracies, color=ny_colors, alpha=0.8,
                edgecolor='black', linewidth=2)
for bar, acc in zip(bars1, ny_accuracies):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.05,
            f'{acc:.2f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax1.set_xticks(range(len(ny_display)))
ax1.set_xticklabels(ny_display, rotation=45, ha='right', fontsize=10)
ax1.set_ylabel('Accuracy (%)', fontsize=11, fontweight='bold')
ax1.set_title('Scenario 1: Universal NY Model\n(Deploy to all cities)', 
              fontsize=12, fontweight='bold')
ax1.set_ylim([96, 100])
ax1.axhline(y=97, color='green', linestyle='--', linewidth=1.5, alpha=0.5)
ax1.grid(True, alpha=0.3, axis='y')

best_models = {}
for city in cities:
    city_acc = training_results[city]['final_accuracy']
    transfers_to = [t for t in transfer_results if t['target'] == city]
    if transfers_to:
        best_transfer = max(transfers_to, key=lambda x: x['zero_shot_acc'])
        if best_transfer['zero_shot_acc'] >= city_acc:
            best_models[city] = (best_transfer['source'], best_transfer['zero_shot_acc'])
        else:
            best_models[city] = (city, city_acc)
    else:
        best_models[city] = (city, city_acc)

best_accs = [best_models[city][1] for city in cities]
best_sources = [best_models[city][0] for city in cities]
best_colors = [city_colors[src] for src in best_sources]
best_display = [city_display_names[c] for c in cities]

bars2 = ax2.bar(range(len(best_display)), best_accs, color=best_colors, alpha=0.8,
                edgecolor='black', linewidth=2)
for bar, acc in zip(bars2, best_accs):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.05,
            f'{acc:.2f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax2.set_xticks(range(len(best_display)))
ax2.set_xticklabels(best_display, rotation=45, ha='right', fontsize=10)
ax2.set_ylabel('Accuracy (%)', fontsize=11, fontweight='bold')
ax2.set_title('Scenario 2: Best Model per City\n(Optimized per target)', 
              fontsize=12, fontweight='bold')
ax2.set_ylim([96, 100])
ax2.grid(True, alpha=0.3, axis='y')

city_accs = [training_results[city]['final_accuracy'] for city in cities]
city_colors_list = [city_colors[c] for c in cities]
city_display = [city_display_names[c] for c in cities]

bars3 = ax3.bar(range(len(city_display)), city_accs, color=city_colors_list, alpha=0.8,
                edgecolor='black', linewidth=2)
for bar, acc in zip(bars3, city_accs):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + 0.05,
            f'{acc:.2f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax3.set_xticks(range(len(city_display)))
ax3.set_xticklabels(city_display, rotation=45, ha='right', fontsize=10)
ax3.set_ylabel('Accuracy (%)', fontsize=11, fontweight='bold')
ax3.set_title('Scenario 3: City-Specific Models\n(Dedicated model per city)', 
              fontsize=12, fontweight='bold')
ax3.set_ylim([96, 100])
ax3.grid(True, alpha=0.3, axis='y')

scenario_data = [
    ['Universal\n(NY)', np.mean(ny_accuracies), 1, '437 KB'],
    ['Best per\nCity', np.mean(best_accs), 1, '437 KB'],
    ['City-\nSpecific', np.mean(city_accs), 6, '2.6 MB']
]

scenario_names = [s[0] for s in scenario_data]
scenario_means = [s[1] for s in scenario_data]
scenario_colors = ['#3498db', '#2ecc71', '#e74c3c']

bars4 = ax4.bar(range(len(scenario_names)), scenario_means, 
                color=scenario_colors, alpha=0.8, edgecolor='black', linewidth=2)

for i, (bar, scenario) in enumerate(zip(bars4, scenario_data)):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height + 0.05,
            f'{height:.2f}%\n({scenario[2]} model)\n{scenario[3]}',
            ha='center', va='bottom', fontsize=9, fontweight='bold')

ax4.set_xticks(range(len(scenario_names)))
ax4.set_xticklabels(scenario_names, fontsize=11)
ax4.set_ylabel('Mean Accuracy (%)', fontsize=11, fontweight='bold')
ax4.set_title('Scenario Comparison\n(Mean accuracy across all cities)', 
              fontsize=12, fontweight='bold')
ax4.set_ylim([97, 99])
ax4.grid(True, alpha=0.3, axis='y')

fig.suptitle('Deployment Scenarios - All Cities Analyzed', 
             fontsize=15, fontweight='bold', y=0.995)

plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig11_Deployment_Scenarios_ALL.png', dpi=300, bbox_inches='tight')
print(f"   ✓ MC_Fig11_Deployment_Scenarios_ALL.png - All 3 scenarios compared")
plt.close()

# ============================================================================
# FIGURE 12-15: ADDITIONAL ANALYSIS
# ============================================================================
print("[12/15] Statistical Summary...")
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

all_accuracies = [training_results[city]['final_accuracy'] for city in cities]
all_transfers_acc = [t['zero_shot_acc'] for t in transfer_results]

ax1.hist(all_accuracies, bins=5, alpha=0.7, color='#3498db', edgecolor='black', linewidth=2, label='Training (6)')
ax1.hist(all_transfers_acc, bins=5, alpha=0.7, color='#e74c3c', edgecolor='black', linewidth=2, label='Transfer (10)')
ax1.axvline(x=np.mean(all_accuracies), color='blue', linestyle='--', linewidth=2, label=f'Train Mean: {np.mean(all_accuracies):.2f}%')
ax1.axvline(x=np.mean(all_transfers_acc), color='red', linestyle='--', linewidth=2, label=f'Transfer Mean: {np.mean(all_transfers_acc):.2f}%')
ax1.set_xlabel('Accuracy (%)', fontsize=11, fontweight='bold')
ax1.set_ylabel('Frequency', fontsize=11, fontweight='bold')
ax1.set_title('Accuracy Distribution - All Results', fontsize=12, fontweight='bold')
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3, axis='y')

stats_labels = ['Mean', 'Std Dev', 'Min', 'Max', 'Range']
train_stats = [np.mean(all_accuracies), np.std(all_accuracies), np.min(all_accuracies), np.max(all_accuracies), np.max(all_accuracies) - np.min(all_accuracies)]
transfer_stats = [np.mean(all_transfers_acc), np.std(all_transfers_acc), np.min(all_transfers_acc), np.max(all_transfers_acc), np.max(all_transfers_acc) - np.min(all_transfers_acc)]

x_stats = np.arange(len(stats_labels))
width = 0.35
ax2.bar(x_stats - width/2, train_stats, width, label='Training', color='#3498db', alpha=0.8, edgecolor='black', linewidth=1.5)
ax2.bar(x_stats + width/2, transfer_stats, width, label='Transfer', color='#e74c3c', alpha=0.8, edgecolor='black', linewidth=1.5)
ax2.set_xticks(x_stats)
ax2.set_xticklabels(stats_labels, fontsize=10)
ax2.set_ylabel('Accuracy (%)', fontsize=11, fontweight='bold')
ax2.set_title('Statistical Comparison', fontsize=12, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3, axis='y')

training_data = [training_results[city]['final_accuracy'] for city in cities]
bp1 = ax3.boxplot(training_data, labels=[city_display_names[c][:3] for c in cities], patch_artist=True)
for patch, city in zip(bp1['boxes'], cities):
    patch.set_facecolor(city_colors[city])
    patch.set_alpha(0.7)
ax3.set_ylabel('Accuracy (%)', fontsize=11, fontweight='bold')
ax3.set_title('City Accuracy Distribution', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')

transfer_gaps_by_source = {city: [] for city in cities}
for transfer in transfer_results:
    source_acc = training_results[transfer['source']]['final_accuracy']
    gap = source_acc - transfer['zero_shot_acc']
    transfer_gaps_by_source[transfer['source']].append(gap)

gap_data = [transfer_gaps_by_source[city] for city in cities]
bp2 = ax4.boxplot(gap_data, labels=[city_display_names[c][:3] for c in cities], patch_artist=True)
for patch, city in zip(bp2['boxes'], cities):
    patch.set_facecolor(city_colors[city])
    patch.set_alpha(0.7)
ax4.set_ylabel('Transfer Gap (%)', fontsize=11, fontweight='bold')
ax4.set_title('Transfer Gap Distribution by Source', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3, axis='y')

fig.suptitle('Statistical Analysis - All Cities & Transfer Learning Results', fontsize=15, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig12_Statistical_Summary_ALL.png', dpi=300, bbox_inches='tight')
print(f"   ✓ MC_Fig12_Statistical_Summary_ALL.png - Complete statistics")
plt.close()

print("[13/15] Transfer Feasibility Analysis...")
fig, ax = plt.subplots(figsize=(14, 8))

feasibility = {}
for source_city in cities:
    transfers_from = [t for t in transfer_results if t['source'] == source_city]
    successful = sum(1 for t in transfers_from if t['zero_shot_acc'] >= 97.0)
    feasibility[source_city] = (successful, len(transfers_from))

sources = list(feasibility.keys())
success_counts = [feasibility[s][0] for s in sources]
total_counts = [feasibility[s][1] for s in sources]
percentages = [(s/t)*100 for s, t in zip(success_counts, total_counts)]
colors_list = [city_colors[c] for c in sources]
display_names_list = [city_display_names[c] for c in sources]

x_pos = np.arange(len(sources))
width = 0.35

bars1 = ax.bar(x_pos - width/2, success_counts, width, label='Successful (>=97%)', color=colors_list, alpha=0.8, edgecolor='black', linewidth=2)
bars2 = ax.bar(x_pos + width/2, total_counts, width, label='Total Transfers', color=colors_list, alpha=0.4, edgecolor='black', linewidth=2)

for i, (bar1, bar2, pct) in enumerate(zip(bars1, bars2, percentages)):
    height1 = bar1.get_height()
    ax.text(bar1.get_x() + bar1.get_width()/2., height1 + 0.1, f'{int(height1)}/{int(height2)}\n({pct:.0f}%)', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax.set_xticks(x_pos)
ax.set_xticklabels(display_names_list, rotation=45, ha='right', fontsize=11)
ax.set_ylabel('Number of Transfers', fontsize=13, fontweight='bold')
ax.set_title('Transfer Feasibility - All Cities as Source\n(Success rate for each city)', fontsize=14, fontweight='bold', pad=20)
ax.legend(fontsize=11, loc='upper left')
ax.set_ylim([0, 6])
ax.grid(True, alpha=0.3, axis='y', linestyle='--')

plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig13_Transfer_Feasibility_ALL.png', dpi=300, bbox_inches='tight')
print(f"   ✓ MC_Fig13_Transfer_Feasibility_ALL.png - Transfer feasibility analyzed")
plt.close()

print("[14/15] Comprehensive Analysis Dashboard...")
fig = plt.figure(figsize=(18, 10))
gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)

ax1 = fig.add_subplot(gs[0, :2])
city_accs = [training_results[c]['final_accuracy'] for c in cities]
bars = ax1.bar(range(len(cities)), city_accs, color=[city_colors[c] for c in cities], alpha=0.8, edgecolor='black', linewidth=2, width=0.6)
for bar, acc in zip(bars, city_accs):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.05, f'{acc:.2f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax1.set_xticks(range(len(cities)))
ax1.set_xticklabels([city_display_names[c] for c in cities], fontsize=10)
ax1.set_ylabel('Accuracy (%)', fontsize=11, fontweight='bold')
ax1.set_title('All City Accuracies', fontsize=12, fontweight='bold')
ax1.set_ylim([96, 100])
ax1.grid(True, alpha=0.3, axis='y')

ax2 = fig.add_subplot(gs[0, 2])
ax2.axis('off')
stats_text = f"""SUMMARY STATS
Cities: 6
Mean Acc: {np.mean(city_accs):.2f}%
Std Dev: {np.std(city_accs):.2f}%
Best: {max(city_accs):.2f}%
Worst: {min(city_accs):.2f}%

Transfers: 10
T Mean: {np.mean([t['zero_shot_acc'] for t in transfer_results]):.2f}%
Success: {sum(1 for t in transfer_results if t['zero_shot_acc']>=97)}/10
"""
ax2.text(0.05, 0.95, stats_text, transform=ax2.transAxes, fontsize=9, verticalalignment='top', fontfamily='monospace', bbox=dict(boxstyle='round', facecolor='#ecf0f1', alpha=0.8))

ax3 = fig.add_subplot(gs[1, 0])
all_transfer_accs = [t['zero_shot_acc'] for t in transfer_results]
ax3.hist(all_transfer_accs, bins=8, color='#e74c3c', alpha=0.7, edgecolor='black', linewidth=1.5)
ax3.axvline(x=97, color='green', linestyle='--', linewidth=2, label='Target: 97%')
ax3.set_xlabel('Accuracy (%)', fontsize=10, fontweight='bold')
ax3.set_ylabel('Count', fontsize=10, fontweight='bold')
ax3.set_title('Transfer Distribution', fontsize=11, fontweight='bold')
ax3.legend(fontsize=9)
ax3.grid(True, alpha=0.3, axis='y')

ax4 = fig.add_subplot(gs[1, 1])
for city in cities:
    history = training_results[city]['history']
    val_acc = history['val_acc']
    ax4.plot(range(1, len(val_acc)+1), val_acc, linewidth=1.5, color=city_colors[city], alpha=0.6)
ax4.set_xlabel('Epoch', fontsize=10, fontweight='bold')
ax4.set_ylabel('Val Accuracy (%)', fontsize=10, fontweight='bold')
ax4.set_title('Convergence Curves', fontsize=11, fontweight='bold')
ax4.grid(True, alpha=0.3)

ax5 = fig.add_subplot(gs[1, 2])
gaps = [training_results[t['source']]['final_accuracy'] - t['zero_shot_acc'] for t in transfer_results]
ax5.scatter(range(len(gaps)), sorted(gaps), s=100, c=sorted(gaps), cmap='RdYlGn_r', alpha=0.8, edgecolor='black', linewidth=1.5)
ax5.set_xlabel('Transfer (Sorted)', fontsize=10, fontweight='bold')
ax5.set_ylabel('Gap (%)', fontsize=10, fontweight='bold')
ax5.set_title('Transfer Gaps', fontsize=11, fontweight='bold')
ax5.grid(True, alpha=0.3)

fig.suptitle('Comprehensive Multi-City Analysis Dashboard\n(All 6 cities + 10 transfers in unified view)', fontsize=14, fontweight='bold', y=0.98)
plt.savefig(output_dir / 'MC_Fig14_Dashboard_ALL.png', dpi=300, bbox_inches='tight')
print(f"   ✓ MC_Fig14_Dashboard_ALL.png - Comprehensive dashboard")
plt.close()

print("[15/15] Final Transfer Matrix Summary...")
fig, ax = plt.subplots(figsize=(14, 10))

combined_matrix = np.zeros((len(cities), len(cities)))
for i, source_city in enumerate(cities):
    for j, target_city in enumerate(cities):
        if i == j:
            combined_matrix[j, i] = training_results[source_city]['final_accuracy']
        else:
            for transfer in transfer_results:
                if transfer['source'] == source_city and transfer['target'] == target_city:
                    combined_matrix[j, i] = transfer['zero_shot_acc']

im = ax.imshow(combined_matrix, cmap='RdYlGn', aspect='auto', vmin=95.5, vmax=100)

display_names_short = [city_display_names[c] for c in cities]
ax.set_xticks(range(len(cities)))
ax.set_yticks(range(len(cities)))
ax.set_xticklabels(display_names_short, rotation=45, ha='right', fontsize=11)
ax.set_yticklabels(display_names_short, fontsize=11)
ax.set_xlabel('Source City (Model Trained)', fontsize=13, fontweight='bold')
ax.set_ylabel('Target City (Deployment)', fontsize=13, fontweight='bold')
ax.set_title('Complete Transfer Matrix Summary\n(All 36 combinations: diagonal=training, off-diagonal=transfer)', fontsize=14, fontweight='bold', pad=20)

for i in range(len(cities)):
    for j in range(len(cities)):
        color = 'white' if combined_matrix[i, j] < 97.5 else 'black'
        text = ax.text(j, i, f'{combined_matrix[i, j]:.2f}%', ha="center", va="center", color=color, fontsize=10, fontweight='bold')

cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label('Accuracy (%)', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(output_dir / 'MC_Fig15_Final_Matrix_ALL.png', dpi=300, bbox_inches='tight')
print(f"   ✓ MC_Fig15_Final_Matrix_ALL.png - Final matrix summary")
plt.close()

print("\n" + "="*80)
print("✅ ALL 15 UNIFIED VISUALIZATIONS GENERATED SUCCESSFULLY!")
print("="*80)
print(f"\n📁 Output Directory: {output_dir}")
print(f"\n📊 UNIFIED VISUALIZATION FEATURES:")
print(f"   ✓ All 15 images include ALL 6 cities in each plot")
print(f"   ✓ Easy visual comparison across all results")
print(f"   ✓ Complete data visibility in every visualization")
print(f"   ✓ 300 DPI PNG format - publication ready")
print(f"   ✓ Color-coded by city for quick identification")
print(f"\n💡 KEY IMPROVEMENT: Every image now shows ALL city data side-by-side!")
print("="*80)
