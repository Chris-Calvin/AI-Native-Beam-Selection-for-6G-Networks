"""
Configuration Template for Sionna-Transfer Pipeline
Customize these settings to adjust pipeline behavior
"""

# ============================================================================
# HARDWARE & PATHS
# ============================================================================

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent

WORKING_DIR = str(PROJECT_ROOT) + '/'

# Device: 'cpu' for CPU-only, 'cuda' if available
DEVICE = 'cpu'

# Number of parallel threads for CPU
OMP_NUM_THREADS = 4  # Adjust based on your i5 core count


# ============================================================================
# DATA CONFIGURATION
# ============================================================================

# Number of user samples to load per city
NUM_USERS = 10000

# Antenna array configuration (8x8 UPA)
NUM_ANTENNAS = 64
NUM_BEAMS = 64

# Data split for training/validation
TRAIN_SPLIT = 0.8


# ============================================================================
# PHASE 3: NEW YORK TRAINING
# ============================================================================

# Training hyperparameters
NY_EPOCHS = 20
NY_BATCH_SIZE = 64
NY_LEARNING_RATE = 1e-3

# Model architecture
NY_HIDDEN_DIM = 128
NY_MODEL_DEPTH = 3


# ============================================================================
# PHASE 4: TRANSFER LEARNING (LOS ANGELES)
# ============================================================================

# Fine-tuning hyperparameters
LA_EPOCHS = 15
LA_BATCH_SIZE = 32
LA_LEARNING_RATE = 1e-4

# Whether to freeze backbone during fine-tuning
FREEZE_BACKBONE = True

# Few-shot learning: number of samples to test
FEW_SHOT_SAMPLES = [0, 10, 50, 100, 500]


# ============================================================================
# PHASE 5: OPENVINO OPTIMIZATION
# ============================================================================

# OpenVINO precision: 'FP32' or 'FP16'
OPENVINO_PRECISION = 'FP16'

# Number of inference samples for benchmarking
BENCHMARK_ITERATIONS = 1000

# Whether to try GPU (Intel Iris Xe) if available
USE_GPU_IF_AVAILABLE = True


# ============================================================================
# FILE PATHS
# ============================================================================

# Model checkpoints
PATH_MODEL_NY = str(PROJECT_ROOT / 'models' / 'model_ny.pt')
PATH_MODEL_LA = str(PROJECT_ROOT / 'models' / 'model_la_finetuned.pt')

# OpenVINO output directory
PATH_OPENVINO_DIR = str(PROJECT_ROOT / 'models' / 'openvino')

# Visualization output directory
PATH_OUTPUT_DIR = str(PROJECT_ROOT / 'outputs')

# Extracted dataset directories
PATH_DATA_NY = str(PROJECT_ROOT / 'data' / 'NewYork')
PATH_DATA_LA = str(PROJECT_ROOT / 'data' / 'LosAngeles')

# Original zip file locations
_downloads_dir = Path(os.environ.get("DOWNLOADS_DIR", Path.home() / "Downloads"))
PATH_ZIP_NY = str(PROJECT_ROOT / 'city_0_newyork_3p5.zip' if (PROJECT_ROOT / 'city_0_newyork_3p5.zip').exists() else _downloads_dir / 'city_0_newyork_3p5.zip')
PATH_ZIP_LA = str(PROJECT_ROOT / 'city_1_losangeles_3p5.zip' if (PROJECT_ROOT / 'city_1_losangeles_3p5.zip').exists() else _downloads_dir / 'city_1_losangeles_3p5.zip')


# ============================================================================
# VISUALIZATION
# ============================================================================

# DPI for saved figures
FIGURE_DPI = 300

# Figure size (width, height) in inches
FIGURE_SIZE = (10, 8)

# Color scheme: 'default', 'dark', 'colorblind'
COLOR_SCHEME = 'default'


# ============================================================================
# LOGGING & DEBUGGING
# ============================================================================

# Verbosity level: 0 (silent), 1 (normal), 2 (verbose)
VERBOSE = 1

# Save training history plots
SAVE_TRAINING_PLOTS = True

# Profile execution time
PROFILE_EXECUTION = True

# Save all intermediate checkpoints
SAVE_ALL_CHECKPOINTS = False


# ============================================================================
# HELPER FUNCTION
# ============================================================================

def get_config():
    """Return all configuration as a dictionary"""
    config = {
        # Hardware
        'device': DEVICE,
        'omp_num_threads': OMP_NUM_THREADS,
        
        # Data
        'num_users': NUM_USERS,
        'num_antennas': NUM_ANTENNAS,
        'num_beams': NUM_BEAMS,
        'train_split': TRAIN_SPLIT,
        
        # NY Training
        'ny_epochs': NY_EPOCHS,
        'ny_batch_size': NY_BATCH_SIZE,
        'ny_learning_rate': NY_LEARNING_RATE,
        'ny_hidden_dim': NY_HIDDEN_DIM,
        'ny_model_depth': NY_MODEL_DEPTH,
        
        # LA Transfer
        'la_epochs': LA_EPOCHS,
        'la_batch_size': LA_BATCH_SIZE,
        'la_learning_rate': LA_LEARNING_RATE,
        'freeze_backbone': FREEZE_BACKBONE,
        'few_shot_samples': FEW_SHOT_SAMPLES,
        
        # OpenVINO
        'openvino_precision': OPENVINO_PRECISION,
        'benchmark_iterations': BENCHMARK_ITERATIONS,
        'use_gpu_if_available': USE_GPU_IF_AVAILABLE,
        
        # Paths
        'path_model_ny': PATH_MODEL_NY,
        'path_model_la': PATH_MODEL_LA,
        'path_openvino_dir': PATH_OPENVINO_DIR,
        'path_output_dir': PATH_OUTPUT_DIR,
        'path_data_ny': PATH_DATA_NY,
        'path_data_la': PATH_DATA_LA,
        'path_zip_ny': PATH_ZIP_NY,
        'path_zip_la': PATH_ZIP_LA,
        
        # Visualization
        'figure_dpi': FIGURE_DPI,
        'figure_size': FIGURE_SIZE,
        'color_scheme': COLOR_SCHEME,
        
        # Logging
        'verbose': VERBOSE,
        'save_training_plots': SAVE_TRAINING_PLOTS,
        'profile_execution': PROFILE_EXECUTION,
        'save_all_checkpoints': SAVE_ALL_CHECKPOINTS,
    }
    return config


if __name__ == '__main__':
    import json
    config = get_config()
    print('Sionna-Transfer Configuration:')
    print(json.dumps(config, indent=2))
