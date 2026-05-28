# Sionna-Transfer: Complete File Index

## 📚 Documentation Files

### Primary Documentation
- **README.md** - Comprehensive project guide with installation, usage, and troubleshooting
- **QUICK_START.md** - Quick reference for rapid execution
- **PROJECT_SUMMARY.md** - High-level overview of architecture and results
- **FILE_INDEX.md** - This file

### Configuration
- **config.py** - Centralized configuration template with all adjustable parameters
- **requirements.txt** - Python package dependencies

---

## 🔧 Executable Scripts

### Setup & Installation
- **setup.bat** - Automated Windows setup (creates venv, installs dependencies)
- **run_pipeline.bat** - Launches main pipeline with optimization settings
- **diagnostics.py** - System diagnostics (checks hardware, libraries, data)
- **validate_install.py** - Installation validator (checks all components)

### Main Pipeline
- **main.py** - Master orchestration script that runs all 5 phases end-to-end

---

## 📁 Source Code Directory (src/)

### Core Modules
- **__init__.py** - Package initialization with exported functions
- **phase0_extraction.py** - Zip file extraction to working directory
- **phase1_dataloader.py** - DeepMIMO data loading and preprocessing
- **phase3_training.py** - ResMLP architecture and training loop
- **phase4_transfer.py** - Transfer learning, fine-tuning, few-shot learning
- **phase5_openvino.py** - OpenVINO conversion and inference benchmarking
- **visualization.py** - Matplotlib visualization and plot generation

### Module Descriptions

#### phase0_extraction.py
```python
extract_datasets(working_dir)  # Extract NY and LA zips to data folders
```
- Automatically extracts city_0_newyork_3p5.zip
- Automatically extracts city_1_losangeles_3p5.zip
- Creates directory structure

#### phase1_dataloader.py
```python
load_deepmimo_data(city_path, num_users, num_antennas)
prepare_dataset(data, num_samples, num_beams)
```
- Loads channel matrices from extracted data
- Parses parameters.m files
- Normalizes positions and extracts beam labels
- Returns PyTorch tensors ready for training

#### phase3_training.py
```python
class ResMLP(nn.Module)              # Model architecture
train_model(dataset, path, epochs)   # Training function
train_epoch(model, loader, ...)      # Single epoch training
evaluate(model, loader, ...)         # Validation loop
```
- 3-layer residual MLP architecture
- Input: 2D normalized positions
- Output: 64 beam logits
- Includes training and evaluation loops

#### phase4_transfer.py
```python
load_pretrained_model(path)                      # Load checkpoint
freeze_layers(model, freeze_all_but_last)        # Freeze backbone
fine_tune_model(model, dataset, path, ...)       # Fine-tuning
evaluate_zero_shot(model, dataset)               # Zero-shot transfer
few_shot_learning_study(model, dataset, ...)     # Few-shot analysis
```
- Implements zero-shot transfer evaluation
- Fine-tunes with frozen backbone
- Few-shot learning with variable sample sizes
- Generates transfer learning curves

#### phase5_openvino.py
```python
convert_to_openvino(model, ...)             # PyTorch → OpenVINO IR
benchmark_pytorch_cpu(model, ...)           # PyTorch latency
benchmark_openvino(ir_path, ...)            # OpenVINO latency
compare_runtimes(model, ir_path, ...)       # Side-by-side comparison
```
- ONNX intermediate format conversion
- OpenVINO IR format (FP16 optimized)
- CPU and GPU benchmarking
- Speedup calculation

#### visualization.py
```python
plot_city_coverage_map(dataset, predictions)          # Fig 1
plot_generalization_gap(ny_acc, la_acc)              # Fig 2
plot_transfer_learning_curve(few_shot_results)       # Fig 3
plot_inference_speedup(pytorch_lat, ov_lat)          # Fig 4
generate_summary_report(results_dict, output_dir)    # Generate all
```
- Creates 4 publication-quality plots
- 300 DPI PNG output
- Publication-ready formatting

---

## 📊 Data & Output Directories

### data/ (After Extraction)
```
data/
├── NewYork/
│   ├── parameters.m
│   ├── channel_*.npy or .mat
│   └── positions_*.npy or .mat
└── LosAngeles/
    ├── parameters.m
    ├── channel_*.npy or .mat
    └── positions_*.npy or .mat
```

### models/ (After Training)
```
models/
├── model_ny.pt              # 3 MB - NY-trained checkpoint
├── model_la_finetuned.pt    # 3 MB - LA fine-tuned checkpoint
├── model_la_few_shot_10.pt  # Few-shot checkpoints
├── model_la_few_shot_50.pt
├── model_la_few_shot_100.pt
├── model_la_few_shot_500.pt
└── openvino/
    ├── model.xml            # 50 KB - OpenVINO IR definition
    ├── model.bin            # 2 MB - OpenVINO weights
    └── model.onnx           # 2 MB - ONNX intermediate
```

### outputs/ (Visualizations)
```
outputs/
├── Fig1_NY_Coverage_Map.png           # Beam distribution heatmap
├── Fig2_Generalization_Gap.png        # NY vs LA accuracy comparison
├── Fig3_Transfer_Success.png          # Few-shot learning curve
└── Fig4_Intel_Acceleration.png        # Inference speedup chart
```

---

## 🔄 Execution Flow

```
start
  ↓
[setup.bat] → Create venv, install dependencies
  ↓
[diagnostics.py] → System checks (optional)
  ↓
[main.py]
  ├─→ [phase0_extraction.py] → Extract zips
  ├─→ [phase1_dataloader.py] → Load data
  ├─→ [phase3_training.py] → Train NY model
  ├─→ [phase4_transfer.py] → Transfer learning
  ├─→ [phase5_openvino.py] → Export & benchmark
  └─→ [visualization.py] → Generate plots
  ↓
[outputs/] → View results
```

---

## 📋 Quick Reference

### To Run Everything
```bash
cd C:\Research_Data
setup.bat              # First time only
run_pipeline.bat       # Execute pipeline
```

### To Run Specific Phase
```bash
python main.py         # Full pipeline

# Or individual phases
python src/phase0_extraction.py
python src/phase1_dataloader.py
python diagnostics.py
```

### To Validate Installation
```bash
python validate_install.py
python diagnostics.py
```

### To Check Configuration
```bash
python config.py       # Print current settings
```

---

## 🎯 Key Metrics Output by Each Module

### phase3_training.py Output
- Epoch-wise training loss and accuracy
- Validation accuracy progression
- Final model checkpoint saved

### phase4_transfer.py Output
- Zero-shot accuracy (NY model on LA data)
- Few-shot accuracy for each sample size
- Fine-tuning convergence plot

### phase5_openvino.py Output
- Inference latency (ms): PyTorch CPU
- Inference latency (ms): OpenVINO GPU
- Speedup factor (x)

### visualization.py Output
- 4 PNG files in outputs/ directory
- 300 DPI resolution
- Publication-ready quality

---

## 🔧 Configuration Hierarchy

1. **Default** - Hardcoded in each module
2. **config.py** - Template with all adjustable settings
3. **main.py CONFIG dict** - Runtime overrides
4. **Command line** - Future extension point

---

## 📦 Dependency Tree

```
torch
├── numpy
├── scipy
└── ...

openvino
├── numpy
└── ...

matplotlib
├── numpy
└── ...

scikit-learn
├── numpy
└── scipy
```

All installed via `requirements.txt`

---

## 🎨 Visualization Specifications

| Figure | Type | Size | Colors | Key Metric |
|--------|------|------|--------|-----------|
| Fig1 | Scatter | 10x8" | tab20b | Beam index |
| Fig2 | Bar Chart | 10x6" | [Green, Red] | Accuracy (%) |
| Fig3 | Line Plot | 10x6" | Blue/Green | Accuracy (%) |
| Fig4 | Bar Chart | 10x6" | [Red, Green] | Latency (ms) |

---

## ✅ Validation Checklist

Before running pipeline:
- [ ] Python 3.8+ installed
- [ ] All files in place (validate_install.py checks)
- [ ] Virtual environment created (setup.bat does this)
- [ ] Dependencies installed (setup.bat does this)
- [ ] 10+ GB disk space available
- [ ] Windows OS (or adapt paths for Linux/Mac)

---

## 🚨 Error Recovery

### If phase0 fails:
- Check zip paths in Downloads folder
- Pipeline creates synthetic data as fallback

### If phase3 fails:
- Reduce batch_size in CONFIG (32 instead of 64)
- Reduce num_users (2000 instead of 5000)

### If phase5 fails:
- OpenVINO is optional, model works without it
- Pipeline continues if conversion fails

---

## 📞 Support Resources

- **README.md** - Setup and detailed usage
- **QUICK_START.md** - Fast reference
- **config.py** - Configuration documentation
- **Inline comments** - Code-level explanations
- **diagnostics.py** - Troubleshoot system
- **validate_install.py** - Verify setup

---

## 📈 Expected Console Output

```
======================================================================
SIONNA-TRANSFER: 6G BEAM PREDICTION
======================================================================

======================================================================
PHASE 0: EXTRACTING DEEPMIMO DATASETS
======================================================================
✓ NewYork dataset already extracted
✓ LosAngeles dataset already extracted

======================================================================
PHASE 1: LOADING DEEPMIMO DATA
======================================================================
Loaded DeepMIMO data from C:/Research_Data/data/NewYork...
Dataset prepared: torch.Size([5000, 2]) inputs

...

======================================================================
EXECUTION COMPLETE - FINAL SUMMARY
======================================================================

📊 Key Results:
  • NY Model Accuracy: 78.50%
  • LA Zero-Shot Accuracy: 42.30%
  • LA Fine-tuned Accuracy: 85.20%
  • Few-shot Improvement: 43.20%

⚡ Inference Performance:
  • PyTorch CPU: 2.450 ms
  • OpenVINO GPU: 0.890 ms
  • Speedup: 2.75x

📁 Output Files:
  • Models: C:/Research_Data/models/
  • Visualizations: C:/Research_Data/outputs/Fig*.png
  • OpenVINO IR: C:/Research_Data/models/openvino/

✓ Pipeline execution successful!
```

---

**File Index Version:** 1.0
**Last Updated:** January 2026
**Status:** ✅ Complete
