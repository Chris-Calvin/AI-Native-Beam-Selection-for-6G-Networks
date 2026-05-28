"""
Phase 4: Transfer Learning
Fine-tune NY model on LA data with few-shot learning
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
from pathlib import Path

def load_pretrained_model(model_path, device='cpu'):
    """Load pretrained model checkpoint"""
    checkpoint = torch.load(model_path, map_location=device)
    
    # Reconstruct model
    from phase3_training import ResMLP
    config = checkpoint['model_config']
    model = ResMLP(**config)
    model.load_state_dict(checkpoint['model_state'])
    model.to(device)
    
    return model, checkpoint


def freeze_layers(model, freeze_all_but_last=True):
    """Freeze all layers except the last linear layer"""
    if freeze_all_but_last:
        for param in model.parameters():
            param.requires_grad = False
        # Unfreeze output projection layer
        model.output_proj.weight.requires_grad = True
        model.output_proj.bias.requires_grad = True
        print('Froze all layers except output projection')
    
    # Count trainable parameters
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f'Trainable params: {trainable} / {total}')


def fine_tune_model(pretrained_model, target_dataset, model_save_path,
                   epochs=10, batch_size=32, device='cpu', verbose=True,
                   freeze_backbone=True):
    """
    Fine-tune pretrained model on target domain (LA)
    
    Args:
        pretrained_model: Loaded NY model
        target_dataset: LA dataset dict with 'inputs' and 'labels'
        model_save_path: Where to save fine-tuned model
        epochs: Fine-tuning epochs
        batch_size: Batch size
        device: 'cpu' or 'cuda'
        verbose: Print logs
        freeze_backbone: Whether to freeze non-output layers
        
    Returns:
        dict: Fine-tuning history and updated model
    """
    # Freeze backbone if requested
    if freeze_backbone:
        freeze_layers(pretrained_model, freeze_all_but_last=True)
    
    inputs, labels = target_dataset['inputs'], target_dataset['labels']
    
    # Create data loader
    dataset = TensorDataset(inputs, labels)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    # Optimizer (only for unfrozen params)
    optimizer = optim.Adam(
        [p for p in pretrained_model.parameters() if p.requires_grad],
        lr=1e-4  # Lower learning rate for fine-tuning
    )
    criterion = nn.CrossEntropyLoss()
    
    history = {
        'loss': [],
        'acc': []
    }
    
    if verbose:
        print(f'\nFine-tuning on target domain (device: {device})')
        print(f'Samples: {len(inputs)}, Epochs: {epochs}')
        print('-' * 60)
    
    # Fine-tuning loop
    for epoch in range(epochs):
        pretrained_model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for batch_x, batch_y in loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            
            logits = pretrained_model(batch_x)
            loss = criterion(logits, batch_y)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            _, predicted = torch.max(logits, 1)
            correct += (predicted == batch_y).sum().item()
            total += batch_y.size(0)
        
        avg_loss = total_loss / len(loader)
        accuracy = 100 * correct / total
        
        history['loss'].append(avg_loss)
        history['acc'].append(accuracy)
        
        if verbose and (epoch + 1) % 5 == 0 or epoch == 0:
            print(f'Epoch {epoch+1:3d} | Loss: {avg_loss:.4f} | Accuracy: {accuracy:.2f}%')
    
    # Save fine-tuned model
    Path(model_save_path).parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        'model_state': pretrained_model.state_dict(),
        'model_config': {
            'input_dim': 2, 'output_dim': 64, 'hidden_dim': 128, 'depth': 3
        },
        'history': history,
        'source_domain': 'NewYork',
        'target_domain': 'LosAngeles'
    }, model_save_path)
    
    if verbose:
        print(f'[OK] Fine-tuned model saved to {model_save_path}')
    
    return {
        'model': pretrained_model,
        'history': history,
        'final_accuracy': accuracy
    }


def evaluate_zero_shot(source_model, target_dataset, device='cpu'):
    """
    Zero-shot transfer: Test NY model directly on LA data
    
    Args:
        source_model: Trained NY model
        target_dataset: LA dataset dict
        device: Device to use
        
    Returns:
        float: Zero-shot accuracy (%)
    """
    source_model.eval()
    inputs, labels = target_dataset['inputs'], target_dataset['labels']
    
    loader = DataLoader(
        TensorDataset(inputs, labels),
        batch_size=64,
        shuffle=False
    )
    
    correct = 0
    total = 0
    
    with torch.no_grad():
        for batch_x, batch_y in loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            logits = source_model(batch_x)
            _, predicted = torch.max(logits, 1)
            correct += (predicted == batch_y).sum().item()
            total += batch_y.size(0)
    
    zero_shot_acc = 100 * correct / total
    print(f'Zero-shot accuracy (NY model on LA data): {zero_shot_acc:.2f}%')
    
    return zero_shot_acc


def few_shot_learning_study(source_model, target_dataset, device='cpu',
                           sample_sizes=[0, 10, 50, 100, 500]):
    """
    Study accuracy vs number of training samples (few-shot learning)
    
    Args:
        source_model: Pretrained NY model
        target_dataset: LA dataset
        device: Device to use
        sample_sizes: List of num samples to test
        
    Returns:
        dict: Accuracy for each sample size
    """
    results = {}
    inputs, labels = target_dataset['inputs'], target_dataset['labels']
    
    for n_samples in sample_sizes:
        if n_samples == 0:
            # Zero-shot: use source model directly
            acc = evaluate_zero_shot(source_model, target_dataset, device)
            results[n_samples] = acc
        else:
            # Few-shot: fine-tune on subset
            if n_samples > len(inputs):
                print(f'Skipping n_samples={n_samples} (exceeds dataset size)')
                continue
            
            indices = torch.randperm(len(inputs))[:n_samples]
            subset = {
                'inputs': inputs[indices],
                'labels': labels[indices]
            }
            
            # Clone model for this experiment
            import copy
            model_copy = copy.deepcopy(source_model)
            model_copy.to(device)
            
            project_root = Path(__file__).resolve().parent.parent
            models_dir = project_root / 'models'
            models_dir.mkdir(parents=True, exist_ok=True)
            
            result = fine_tune_model(
                model_copy,
                subset,
                str(models_dir / f'model_la_few_shot_{n_samples}.pt'),
                epochs=20,
                batch_size=min(16, n_samples),
                device=device,
                verbose=False,
                freeze_backbone=True
            )
            
            results[n_samples] = result['final_accuracy']
            print(f'  Few-shot (n={n_samples:3d}): Accuracy = {result["final_accuracy"]:.2f}%')
    
    return results


if __name__ == '__main__':
    print('Phase 4: Transfer Learning')
    print('-' * 50)
    
    # Create synthetic models/data for testing
    print('(Use with loaded models and datasets)')
