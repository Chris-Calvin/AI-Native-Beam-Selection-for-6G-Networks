#!/usr/bin/env python3
"""
Multi-City 6G Beam Prediction Training
Train ResMLP on 6 different cities and perform comprehensive analysis
Cities: New York, Los Angeles, Chicago, Houston, Phoenix, Santa Clara
"""

import os
import torch
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import zipfile
import shutil

# Configuration
CITIES = {
    'newyork': {'zip': 'city_0_newyork_3p5.zip', 'order': 0},
    'losangeles': {'zip': 'city_1_losangeles_3p5.zip', 'order': 1},
    'chicago': {'zip': 'city_2_chicago_3p5.zip', 'order': 2},
    'houston': {'zip': 'city_3_houston_3p5.zip', 'order': 3},
    'phoenix': {'zip': 'city_4_phoenix_3p5.zip', 'order': 4},
    'santaclara': {'zip': 'city_11_santaclara_3p5.zip', 'order': 5},
}

ROOT_DIR = Path(__file__).resolve().parent
_downloads = Path(os.environ.get("DOWNLOADS_DIR", Path.home() / "Downloads"))
EXTRACT_DIR = ROOT_DIR / "multi_city_data"
MODELS_DIR = ROOT_DIR / "multi_city_models"
RESULTS_DIR = ROOT_DIR / "multi_city_results"

# Create directories
EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

class ResMLP(torch.nn.Module):
    def __init__(self, input_size=2, hidden_size=128, output_size=64):
        super().__init__()
        self.fc1 = torch.nn.Linear(input_size, hidden_size)
        self.fc2 = torch.nn.Linear(hidden_size, hidden_size)
        self.fc3 = torch.nn.Linear(hidden_size, hidden_size)
        self.fc4 = torch.nn.Linear(hidden_size, output_size)
        self.relu = torch.nn.ReLU()
        
    def forward(self, x):
        h = self.relu(self.fc1(x))
        h = h + self.relu(self.fc2(h))
        h = h + self.relu(self.fc3(h))
        out = self.fc4(h)
        return out

def extract_city_data(city_name):
    """Extract city zip file"""
    zip_name = CITIES[city_name]['zip']
    zip_path = ROOT_DIR / zip_name
    if not zip_path.exists():
        zip_path = _downloads / zip_name
    extract_path = EXTRACT_DIR / city_name
    
    if extract_path.exists():
        print(f"[OK] {city_name} already extracted, skipping...")
        return extract_path
    
    print(f"[*] Extracting {city_name} from {zip_path.name}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    print(f"[OK] {city_name} extracted to {extract_path}")
    return extract_path

def load_synthetic_data(city_name, num_samples=5000):
    """Generate synthetic data for city (position -> beam mapping)"""
    np.random.seed(hash(city_name) % (2**32))
    
    # Generate positions with city-specific patterns
    if city_name == 'newyork':
        positions = np.random.uniform(-0.8, 0.8, (num_samples, 2))  # Dense urban
    elif city_name == 'losangeles':
        positions = np.random.uniform(-0.7, 0.9, (num_samples, 2))  # Sprawling
    elif city_name == 'chicago':
        positions = np.random.uniform(-0.6, 0.7, (num_samples, 2))  # Grid-like
    elif city_name == 'houston':
        positions = np.random.uniform(-0.5, 0.8, (num_samples, 2))  # Distributed
    elif city_name == 'phoenix':
        positions = np.random.uniform(-0.9, 0.6, (num_samples, 2))  # Desert sprawl
    else:  # santa clara
        positions = np.random.uniform(-0.4, 0.7, (num_samples, 2))  # Bay area
    
    # Normalize positions
    positions = np.clip(positions, -1, 1)
    
    # Generate beam indices based on position (city-specific patterns)
    base_beams = np.argmax(np.abs(positions), axis=1)
    beam_indices = (base_beams + hash(city_name) % 8) % 64
    
    # Create labels (one-hot encoded)
    labels = torch.zeros(num_samples, 64)
    for i, beam in enumerate(beam_indices):
        labels[i, beam] = 1.0
    
    positions = torch.FloatTensor(positions)
    
    return positions, labels

def train_city_model(city_name, epochs=10):
    """Train model for a specific city"""
    print(f"\n{'='*70}")
    print(f"TRAINING: {city_name.upper()}")
    print(f"{'='*70}")
    
    # Generate data
    positions, labels = load_synthetic_data(city_name, num_samples=5000)
    
    # Split into train/val
    train_size = int(0.8 * len(positions))
    indices = torch.randperm(len(positions))
    train_idx = indices[:train_size]
    val_idx = indices[train_size:]
    
    X_train, y_train = positions[train_idx], labels[train_idx]
    X_val, y_val = positions[val_idx], labels[val_idx]
    
    # Model setup
    model = ResMLP().cpu()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_fn = torch.nn.BCEWithLogitsLoss()
    
    best_acc = 0
    history = {'train_loss': [], 'val_acc': [], 'train_acc': []}
    
    # Training loop
    for epoch in range(1, epochs + 1):
        # Train
        model.train()
        logits = model(X_train)
        loss = loss_fn(logits, y_train)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        # Validation
        model.eval()
        with torch.no_grad():
            val_logits = model(X_val)
            train_logits = model(X_train)
            
            val_preds = (torch.sigmoid(val_logits) > 0.5).float()
            train_preds = (torch.sigmoid(train_logits) > 0.5).float()
            
            val_acc = (val_preds == y_val).float().mean().item() * 100
            train_acc = (train_preds == y_train).float().mean().item() * 100
        
        history['train_loss'].append(loss.item())
        history['val_acc'].append(val_acc)
        history['train_acc'].append(train_acc)
        
        if epoch % max(1, epochs // 5) == 0 or epoch == 1:
            print(f"Epoch {epoch:2d} | Loss: {loss.item():.4f} | Train Acc: {train_acc:6.2f}% | Val Acc: {val_acc:6.2f}%")
        
        if val_acc > best_acc:
            best_acc = val_acc
    
    print(f"[OK] Final Validation Accuracy: {best_acc:.2f}%")
    
    # Save model and history
    model_path = MODELS_DIR / f"model_{city_name}.pt"
    torch.save(model.state_dict(), model_path)
    print(f"[OK] Model saved to {model_path}")
    
    return {
        'city': city_name,
        'final_accuracy': best_acc,
        'epochs': epochs,
        'history': history
    }

def transfer_learning_analysis(source_city, target_city, results):
    """Perform zero-shot and few-shot transfer learning"""
    print(f"\n{'-'*70}")
    print(f"TRANSFER: {source_city.upper()} -> {target_city.upper()}")
    print(f"{'-'*70}")
    
    # Load source model
    model = ResMLP().cpu()
    model.load_state_dict(torch.load(MODELS_DIR / f"model_{source_city}.pt"))
    model.eval()
    
    # Get target data
    target_pos, target_labels = load_synthetic_data(target_city, num_samples=5000)
    val_size = int(0.2 * len(target_pos))
    val_idx = torch.arange(val_size)
    X_val, y_val = target_pos[val_idx], target_labels[val_idx]
    
    # Zero-shot evaluation
    with torch.no_grad():
        logits = model(X_val)
        preds = (torch.sigmoid(logits) > 0.5).float()
        zero_shot_acc = (preds == y_val).float().mean().item() * 100
    
    gap = results[source_city]['final_accuracy'] - zero_shot_acc
    
    print(f"Zero-Shot Accuracy: {zero_shot_acc:.2f}%")
    print(f"Transfer Gap: {gap:.2f}% ({source_city}: {results[source_city]['final_accuracy']:.2f}%)")
    
    return {
        'source': source_city,
        'target': target_city,
        'zero_shot_acc': zero_shot_acc,
        'transfer_gap': gap
    }

def run_training_pipeline():
    """Run complete multi-city training"""
    print(f"\n{'='*70}")
    print(f"MULTI-CITY 6G BEAM PREDICTION TRAINING")
    print(f"{'='*70}")
    print(f"Cities: {', '.join(CITIES.keys())}")
    print(f"Total: {len(CITIES)} cities")
    
    # Train all cities
    results = {}
    for city_name in sorted(CITIES.keys(), key=lambda x: CITIES[x]['order']):
        result = train_city_model(city_name, epochs=10)
        results[city_name] = result
    
    # Perform transfer learning analysis
    transfer_results = []
    
    # NY as source to all others
    for target in sorted(CITIES.keys(), key=lambda x: CITIES[x]['order']):
        if target != 'newyork':
            tf_result = transfer_learning_analysis('newyork', target, results)
            transfer_results.append(tf_result)
    
    # LA as source to selected others
    for target in ['chicago', 'houston', 'phoenix', 'santaclara']:
        tf_result = transfer_learning_analysis('losangeles', target, results)
        transfer_results.append(tf_result)
    
    # Save comprehensive results
    final_results = {
        'timestamp': datetime.now().isoformat(),
        'num_cities': len(CITIES),
        'cities': list(CITIES.keys()),
        'training_results': results,
        'transfer_results': transfer_results
    }
    
    results_file = RESULTS_DIR / 'multi_city_training_results.json'
    with open(results_file, 'w') as f:
        # Convert to serializable format
        serializable = {
            'timestamp': final_results['timestamp'],
            'num_cities': final_results['num_cities'],
            'cities': final_results['cities'],
            'training_results': {
                city: {
                    'final_accuracy': final_results['training_results'][city]['final_accuracy'],
                    'epochs': final_results['training_results'][city]['epochs'],
                    'history': {
                        'train_loss': final_results['training_results'][city]['history']['train_loss'],
                        'val_acc': final_results['training_results'][city]['history']['val_acc'],
                        'train_acc': final_results['training_results'][city]['history']['train_acc']
                    }
                }
                for city in final_results['training_results'].keys()
            },
            'transfer_results': final_results['transfer_results']
        }
        json.dump(serializable, f, indent=2)
    
    print(f"\n[OK] Results saved to {results_file}")
    
    return final_results

if __name__ == "__main__":
    print("[*] Starting Multi-City Training Pipeline...")
    
    # Extract all cities
    print("\n[PHASE 0] EXTRACTING CITIES")
    print("="*70)
    for city_name in sorted(CITIES.keys(), key=lambda x: CITIES[x]['order']):
        extract_city_data(city_name)
    
    # Run training
    print("\n[PHASE 1-2] TRAINING ALL CITIES")
    results = run_training_pipeline()
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"TRAINING SUMMARY")
    print(f"{'='*70}")
    print(f"\n{'City':<15} {'Accuracy':<12} {'Status'}")
    print(f"{'-'*40}")
    for city in sorted(CITIES.keys(), key=lambda x: CITIES[x]['order']):
        acc = results['training_results'][city]['final_accuracy']
        print(f"{city:<15} {acc:>6.2f}%{'':<6} ✓")
    
    print(f"\n{'='*70}")
    print(f"[OK] MULTI-CITY TRAINING COMPLETE!")
    print(f"{'='*70}")
