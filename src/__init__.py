"""
Sionna-Transfer: 6G Beam Prediction Domain Generalization
Domain generalization for beam prediction across different cities (NY → LA)
"""

__version__ = '1.0.0'
__author__ = '6G Research Team'

from .phase0_extraction import extract_datasets
from .phase1_dataloader import load_deepmimo_data, prepare_dataset
from .phase3_training import ResMLP, train_model
from .phase4_transfer import fine_tune_model, evaluate_zero_shot, few_shot_learning_study
from .phase5_openvino import convert_to_openvino, compare_runtimes
from .visualization import generate_summary_report

__all__ = [
    'extract_datasets',
    'load_deepmimo_data',
    'prepare_dataset',
    'ResMLP',
    'train_model',
    'fine_tune_model',
    'evaluate_zero_shot',
    'few_shot_learning_study',
    'convert_to_openvino',
    'compare_runtimes',
    'generate_summary_report'
]
