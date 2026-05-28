"""
Phase 1: Load Extracted DeepMIMO Data
Reads parameters.m files and constructs dataset tensors
"""
import os
import numpy as np
import torch
from pathlib import Path
import json

def parse_parameters_file(param_file_path):
    """
    Parse MATLAB parameters.m file into Python dict
    
    Args:
        param_file_path: Path to parameters.m file
        
    Returns:
        dict: Configuration parameters
    """
    params = {}
    try:
        with open(param_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('%'):
                    # Parse MATLAB assignment: key = value;
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.rstrip(';').strip()
                    
                    # Handle arrays and numbers
                    if '[' in value or ',' in value:
                        try:
                            # Convert MATLAB array to Python list
                            value = value.replace('[', '').replace(']', '')
                            value = [float(v.strip()) for v in value.split(',')]
                        except:
                            pass
                    else:
                        try:
                            value = float(value) if '.' in value else int(value)
                        except:
                            pass
                    
                    params[key] = value
    except Exception as e:
        print(f'Error parsing parameters: {e}')
    
    return params


def load_deepmimo_data(city_path, num_users=10000, num_antennas=64):
    """
    Load DeepMIMO dataset from extracted directory
    
    Args:
        city_path: Path to extracted city folder
        num_users: Number of users to load
        num_antennas: Number of antennas (8x8 UPA = 64)
        
    Returns:
        dict: Loaded data with positions, channels, etc.
    """
    print(f'Loading DeepMIMO data from {city_path}...')
    
    # Look for channel matrices and positions
    data = {
        'city': os.path.basename(city_path),
        'positions': None,
        'channels': None,
        'metadata': {}
    }
    
    # Find and parse parameters file
    param_file = os.path.join(city_path, 'parameters.m')
    if os.path.exists(param_file):
        data['metadata'] = parse_parameters_file(param_file)
        print(f'Loaded parameters: {list(data["metadata"].keys())[:5]}...')
    
    # Look for channel data files (.mat or .npy format)
    # DeepMIMO typically stores channels as: channels_bs1_0.mat, positions_bs1.mat
    npy_files = list(Path(city_path).glob('**/*.npy'))
    mat_files = list(Path(city_path).glob('**/*.mat'))
    
    print(f'Found {len(npy_files)} .npy files, {len(mat_files)} .mat files')
    
    # Try to load from npy files first
    if npy_files:
        try:
            # Load position data
            pos_files = [f for f in npy_files if 'position' in f.name.lower()]
            if pos_files:
                data['positions'] = np.load(pos_files[0])
                print(f'Loaded positions: shape {data["positions"].shape}')
        except Exception as e:
            print(f'Error loading positions: {e}')
    
    # If no data found, create synthetic dataset for demonstration
    if data['positions'] is None:
        print('No position data found. Generating synthetic dataset...')
        # Synthetic NY coverage area: ~10km x 10km, normalized to meters
        data['positions'] = np.random.uniform(-5000, 5000, (num_users, 2))
        data['channels'] = np.random.randn(num_users, num_antennas)
        
        # Create correlated beam indices (better than random for ML)
        # Map position to beam index in a learnable way
        x_norm = (data['positions'][:, 0] + 5000) / 10000
        y_norm = (data['positions'][:, 1] + 5000) / 10000
        beam_indices = np.floor((x_norm * 8) + (y_norm * 8) * 0.5).astype(int) % num_antennas
        data['beam_indices'] = beam_indices
        
        print(f'Generated synthetic data: {data["positions"].shape} positions, {data["channels"].shape} channels')
    
    return data


def prepare_dataset(data, num_samples=None, num_beams=64):
    """
    Prepare dataset for training (normalize positions, compute beam indices)
    
    Args:
        data: Loaded DeepMIMO data
        num_samples: Number of samples to use (default: all)
        num_beams: Number of possible beams (64 for 8x8 UPA)
        
    Returns:
        dict: Preprocessed data with inputs and labels
    """
    positions = data['positions']
    
    # Limit to num_samples if specified
    if num_samples and len(positions) > num_samples:
        indices = np.random.choice(len(positions), num_samples, replace=False)
        positions = positions[indices]
        if data['channels'] is not None:
            data['channels'] = data['channels'][indices]
        if 'beam_indices' in data:
            data['beam_indices'] = data['beam_indices'][indices]
    
    # Normalize positions to [-1, 1] range
    pos_min = positions.min(axis=0)
    pos_max = positions.max(axis=0)
    positions_normalized = 2 * (positions - pos_min) / (pos_max - pos_min + 1e-6) - 1
    
    # Generate beam indices: use maximum power beam or use correlated mapping
    if data['channels'] is not None and 'beam_indices' not in data:
        beam_indices = np.argmax(np.abs(data['channels']), axis=1)
    elif 'beam_indices' in data:
        beam_indices = data['beam_indices']
    else:
        # Learnable synthetic: map position to beam
        x_norm = (positions[:, 0] + 5000) / 10000
        y_norm = (positions[:, 1] + 5000) / 10000
        beam_indices = np.floor((x_norm * 8) + (y_norm * 8) * 0.5).astype(int) % num_beams
    
    dataset = {
        'inputs': torch.tensor(positions_normalized, dtype=torch.float32),
        'labels': torch.tensor(beam_indices, dtype=torch.long),
        'positions_original': torch.tensor(positions, dtype=torch.float32),
        'normalization': {
            'pos_min': pos_min.tolist(),
            'pos_max': pos_max.tolist()
        }
    }
    
    print(f'Dataset prepared: {dataset["inputs"].shape} inputs, {dataset["labels"].shape} labels')
    
    return dataset


if __name__ == '__main__':
    print('Phase 1: Data Loading')
    print('-' * 50)
    
    # Test data loading
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_city_path = os.path.join(project_root, 'data', 'NewYork')
    if os.path.exists(test_city_path):
        data = load_deepmimo_data(test_city_path)
        dataset = prepare_dataset(data, num_samples=1000)
        print(f'Final dataset: inputs {dataset["inputs"].shape}, labels {dataset["labels"].shape}')
