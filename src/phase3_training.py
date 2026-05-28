"""
Phase 2 & 3: Feature Engineering + Model Training
Includes ResMLP architecture and training loop
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
from pathlib import Path

class ResMLP(nn.Module):
    """
    Residual MLP for Beam Prediction
    Input: 2D (normalized user location x, y)
    Output: 64 (beam logits)
    """
    def __init__(self, input_dim=2, output_dim=64, hidden_dim=128, depth=3):
        super(ResMLP, self).__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        
        # Input projection
        self.input_proj = nn.Linear(input_dim, hidden_dim)
        
        # Residual blocks
        self.residual_blocks = nn.ModuleList()
        for _ in range(depth):
            block = nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, hidden_dim),
                nn.ReLU()
            )
            self.residual_blocks.append(block)
        
        # Output projection
        self.output_proj = nn.Linear(hidden_dim, output_dim)
    
    def forward(self, x):
        """Forward pass with residual connections"""
        h = self.input_proj(x)  # [batch, hidden_dim]
        
        for block in self.residual_blocks:
            h = h + block(h)  # Residual connection
        
        logits = self.output_proj(h)  # [batch, output_dim]
        return logits


def train_epoch(model, train_loader, optimizer, criterion, device='cpu'):
    """Train for one epoch"""
    model.train()
    total_loss = 0
    correct = 0
    total = 0
    
    for batch_x, batch_y in train_loader:
        batch_x, batch_y = batch_x.to(device), batch_y.to(device)
        
        # Forward
        logits = model(batch_x)
        loss = criterion(logits, batch_y)
        
        # Backward
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        # Metrics
        total_loss += loss.item()
        _, predicted = torch.max(logits, 1)
        correct += (predicted == batch_y).sum().item()
        total += batch_y.size(0)
    
    avg_loss = total_loss / len(train_loader)
    accuracy = 100 * correct / total
    
    return avg_loss, accuracy


def evaluate(model, test_loader, criterion, device='cpu'):
    """Evaluate model on test set"""
    model.eval()
    total_loss = 0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for batch_x, batch_y in test_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            
            total_loss += loss.item()
            _, predicted = torch.max(logits, 1)
            correct += (predicted == batch_y).sum().item()
            total += batch_y.size(0)
    
    avg_loss = total_loss / len(test_loader)
    accuracy = 100 * correct / total
    
    return avg_loss, accuracy


def train_model(dataset, model_save_path, epochs=20, batch_size=64, 
                train_split=0.8, device='cpu', verbose=True):
    """
    Train ResMLP model on dataset
    
    Args:
        dataset: Dict with 'inputs' and 'labels' tensors
        model_save_path: Where to save trained model
        epochs: Number of training epochs
        batch_size: Training batch size
        train_split: Fraction for training (rest is validation)
        device: 'cpu' or 'cuda'
        verbose: Print training logs
        
    Returns:
        dict: Training history and trained model
    """
    inputs, labels = dataset['inputs'], dataset['labels']
    
    # Split dataset
    num_train = int(len(inputs) * train_split)
    indices = torch.randperm(len(inputs))
    train_indices = indices[:num_train]
    val_indices = indices[num_train:]
    
    train_dataset = TensorDataset(inputs[train_indices], labels[train_indices])
    val_dataset = TensorDataset(inputs[val_indices], labels[val_indices])
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # Model, optimizer, loss
    model = ResMLP(input_dim=2, output_dim=64, hidden_dim=128, depth=3)
    model.to(device)
    
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()
    
    history = {
        'train_loss': [],
        'train_acc': [],
        'val_loss': [],
        'val_acc': []
    }
    
    if verbose:
        print(f'Training ResMLP (device: {device})')
        print(f'Train samples: {len(train_indices)}, Val samples: {len(val_indices)}')
        print('-' * 60)
    
    # Training loop
    for epoch in range(epochs):
        train_loss, train_acc = train_epoch(model, train_loader, optimizer, criterion, device)
        val_loss, val_acc = evaluate(model, val_loader, criterion, device)
        
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        
        if verbose and (epoch + 1) % 5 == 0 or epoch == 0:
            print(f'Epoch {epoch+1:3d} | Train Loss: {train_loss:.4f} | '
                  f'Train Acc: {train_acc:.2f}% | Val Acc: {val_acc:.2f}%')
    
    # Save model
    Path(model_save_path).parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        'model_state': model.state_dict(),
        'model_config': {'input_dim': 2, 'output_dim': 64, 'hidden_dim': 128, 'depth': 3},
        'history': history
    }, model_save_path)
    
    if verbose:
        print(f'[OK] Model saved to {model_save_path}')
    
    return {'model': model, 'history': history, 'loader': val_loader}


if __name__ == '__main__':
    print('Phase 2 & 3: Feature Engineering + Model Training')
    print('-' * 50)
    
    # Create synthetic dataset for testing
    X = torch.randn(1000, 2)
    y = torch.randint(0, 64, (1000,))
    dataset = {'inputs': X, 'labels': y}
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_save_dir = os.path.join(project_root, 'models')
    os.makedirs(model_save_dir, exist_ok=True)
    result = train_model(dataset, os.path.join(model_save_dir, 'model_ny.pt'), epochs=10)
    print(f'Training complete. Final val accuracy: {result["history"]["val_acc"][-1]:.2f}%')
