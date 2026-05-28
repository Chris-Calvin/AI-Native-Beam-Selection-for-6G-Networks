"""
Main Orchestration Script
Runs all phases end-to-end: NY training → LA transfer → OpenVINO export
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import torch
import numpy as np

# Import phase modules
from phase0_extraction import extract_datasets
from phase1_dataloader import load_deepmimo_data, prepare_dataset
from phase3_training import train_model, ResMLP
from phase4_transfer import (
    load_pretrained_model,
    fine_tune_model,
    evaluate_zero_shot,
    few_shot_learning_study
)
from phase5_openvino import convert_to_openvino, compare_runtimes
from visualization import generate_summary_report

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent

# Configuration
CONFIG = {
    'working_dir': str(PROJECT_ROOT) + '/',
    'device': 'cpu',  # CPU-optimized for Intel i5 + Iris Xe
    'num_users': 10000,
    'num_antennas': 64,
    'num_beams': 64,
    
    # Training
    'ny_epochs': 10,
    'la_epochs': 8,
    'batch_size': 64,
    'train_split': 0.8,
    
    # Transfer learning
    'few_shot_samples': [0, 10, 50, 100, 500],
    
    # Paths
    'model_ny': str(PROJECT_ROOT / 'models' / 'model_ny.pt'),
    'model_la': str(PROJECT_ROOT / 'models' / 'model_la_finetuned.pt'),
    'openvino_dir': str(PROJECT_ROOT / 'models' / 'openvino'),
    'output_dir': str(PROJECT_ROOT / 'outputs')
}



def main():
    """Main pipeline"""
    print('\n' + '='*70)
    print('SIONNA-TRANSFER: 6G BEAM PREDICTION WITH DOMAIN GENERALIZATION')
    print('='*70)
    print(f'Device: {CONFIG["device"].upper()} (Intel i5 + Iris Xe)')
    print(f'Working Directory: {CONFIG["working_dir"]}')
    
    # =========================================================================
    # PHASE 0: EXTRACTION
    # =========================================================================
    print('\n' + '='*70)
    print('PHASE 0: EXTRACTING DEEPMIMO DATASETS')
    print('='*70)
    extracted_paths = extract_datasets(CONFIG['working_dir'])
    
    if not extracted_paths:
        print('\n✗ No datasets extracted. Please check zip file paths.')
        print(f'Expected locations:')
        print(f'  - {PROJECT_ROOT / "city_0_newyork_3p5.zip"}')
        print(f'  - {PROJECT_ROOT / "city_1_losangeles_3p5.zip"}')
        print(f'  - or your user Downloads folder')
        print('\nCreating synthetic datasets for demonstration...')
        
        # Create synthetic data if zips not found
        ny_path = os.path.join(CONFIG['working_dir'], 'data', 'NewYork')
        la_path = os.path.join(CONFIG['working_dir'], 'data', 'LosAngeles')
        os.makedirs(ny_path, exist_ok=True)
        os.makedirs(la_path, exist_ok=True)
        extracted_paths = {'NewYork': ny_path, 'LosAngeles': la_path}
    
    # =========================================================================
    # PHASE 1: DATA LOADING
    # =========================================================================
    print('\n' + '='*70)
    print('PHASE 1: LOADING DEEPMIMO DATA')
    print('='*70)
    
    ny_data = load_deepmimo_data(
        extracted_paths['NewYork'],
        num_users=CONFIG['num_users'],
        num_antennas=CONFIG['num_antennas']
    )
    
    la_data = load_deepmimo_data(
        extracted_paths['LosAngeles'],
        num_users=CONFIG['num_users'],
        num_antennas=CONFIG['num_antennas']
    )
    
    # =========================================================================
    # PHASE 2: FEATURE ENGINEERING
    # =========================================================================
    print('\n' + '='*70)
    print('PHASE 2: FEATURE ENGINEERING & DATASET PREPARATION')
    print('='*70)
    
    ny_dataset = prepare_dataset(ny_data, num_samples=5000, num_beams=CONFIG['num_beams'])
    la_dataset = prepare_dataset(la_data, num_samples=5000, num_beams=CONFIG['num_beams'])
    
    # =========================================================================
    # PHASE 3: TRAIN ON SOURCE DOMAIN (NEW YORK)
    # =========================================================================
    print('\n' + '='*70)
    print('PHASE 3: TRAINING ON SOURCE DOMAIN (NEW YORK)')
    print('='*70)
    
    ny_result = train_model(
        ny_dataset,
        CONFIG['model_ny'],
        epochs=CONFIG['ny_epochs'],
        batch_size=CONFIG['batch_size'],
        train_split=CONFIG['train_split'],
        device=CONFIG['device'],
        verbose=True
    )
    
    ny_model = ny_result['model']
    ny_history = ny_result['history']
    ny_accuracy = ny_history['val_acc'][-1]
    
    print(f'\n[OK] NY Model Training Complete')
    print(f'  Final Validation Accuracy: {ny_accuracy:.2f}%')
    
    # =========================================================================
    # PHASE 4: TRANSFER LEARNING
    # =========================================================================
    print('\n' + '='*70)
    print('PHASE 4: TRANSFER LEARNING (NEW YORK → LOS ANGELES)')
    print('='*70)
    
    # Zero-shot transfer
    print('\nEvaluating zero-shot transfer...')
    la_zero_shot_acc = evaluate_zero_shot(ny_model, la_dataset, device=CONFIG['device'])
    
    generalization_gap = ny_accuracy - la_zero_shot_acc
    print(f'Generalization Gap: {generalization_gap:.2f}% (NY: {ny_accuracy:.2f}% → LA: {la_zero_shot_acc:.2f}%)')
    
    # Fine-tune on full LA dataset
    print('\nFine-tuning on full LA dataset...')
    la_result = fine_tune_model(
        ny_model,
        la_dataset,
        CONFIG['model_la'],
        epochs=CONFIG['la_epochs'],
        batch_size=CONFIG['batch_size'],
        device=CONFIG['device'],
        verbose=True,
        freeze_backbone=True
    )
    
    la_accuracy = la_result['final_accuracy']
    print(f'\n[OK] LA Fine-tuning Complete')
    print(f'  Final LA Accuracy: {la_accuracy:.2f}%')
    
    # Few-shot learning study
    print('\nConducting few-shot learning study...')
    few_shot_results = few_shot_learning_study(
        ny_model,
        la_dataset,
        device=CONFIG['device'],
        sample_sizes=CONFIG['few_shot_samples']
    )
    
    print(f'\n[OK] Few-shot Results:')
    for n_samples, acc in sorted(few_shot_results.items()):
        print(f'    {n_samples:3d} samples → {acc:.2f}% accuracy')
    
    # =========================================================================
    # PHASE 5: OPENVINO EXPORT & BENCHMARKING
    # =========================================================================
    print('\n' + '='*70)
    print('PHASE 5: OPENVINO EXPORT & INFERENCE BENCHMARKING')
    print('='*70)
    
    # Load final fine-tuned model
    checkpoint = torch.load(CONFIG['model_la'], map_location=CONFIG['device'])
    final_model = ResMLP(**checkpoint['model_config'])
    final_model.load_state_dict(checkpoint['model_state'])
    final_model.to(CONFIG['device'])
    
    # Convert to OpenVINO
    print('\nConverting to OpenVINO IR format...')
    ir_path = convert_to_openvino(
        final_model,
        input_shape=(1, 2),
        export_dir=CONFIG['openvino_dir'],
        precision='FP16',
        verbose=True
    )
    
    # Benchmark
    print('\nBenchmarking inference performance...')
    benchmark_results = compare_runtimes(final_model, ir_path, num_inferences=1000, verbose=True)
    
    pytorch_latency = benchmark_results['pytorch_cpu']['mean']
    openvino_latency = benchmark_results.get('openvino', {}).get('mean', pytorch_latency)
    
    # =========================================================================
    # VISUALIZATION & REPORTING
    # =========================================================================
    print('\n' + '='*70)
    print('GENERATING VISUALIZATION REPORT')
    print('='*70)
    
    results_dict = {
        'ny_dataset': ny_dataset,
        'ny_predictions': ny_dataset['labels'].numpy(),
        'ny_accuracy': ny_accuracy,
        'la_zero_shot_accuracy': la_zero_shot_acc,
        'few_shot_results': few_shot_results,
        'pytorch_latency': pytorch_latency,
        'openvino_latency': openvino_latency
    }
    
    generate_summary_report(results_dict, CONFIG['output_dir'])
    
    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    print('\n' + '='*70)
    print('EXECUTION COMPLETE - FINAL SUMMARY')
    print('='*70)
    print(f'\nKey Results:')
    print(f'  * NY Model Accuracy: {ny_accuracy:.2f}%')
    print(f'  * LA Zero-Shot Accuracy: {la_zero_shot_acc:.2f}%')
    print(f'  * LA Fine-tuned Accuracy: {la_accuracy:.2f}%')
    print(f'  * Generalization Gap: {generalization_gap:.2f}%')
    print(f'  * Few-shot Improvement (0->100 samples): {few_shot_results[100] - few_shot_results[0]:.2f}%')
    
    print(f'\nInference Performance:')
    print(f'  * PyTorch CPU: {pytorch_latency:.3f} ms')
    print(f'  * OpenVINO GPU: {openvino_latency:.3f} ms')
    print(f'  * Speedup: {pytorch_latency/openvino_latency:.2f}x')
    
    print(f'\nOutput Files:')
    print(f'  * Models: {CONFIG["working_dir"]}/models/')
    print(f'  * Visualizations: {CONFIG["output_dir"]}/Fig*.png')
    print(f'  * OpenVINO IR: {CONFIG["openvino_dir"]}/model.*')
    
    print('\n[OK] Pipeline execution successful!')
    print('='*70 + '\n')


if __name__ == '__main__':
    main()
