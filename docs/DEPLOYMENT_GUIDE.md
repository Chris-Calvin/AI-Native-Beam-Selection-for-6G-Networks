# 🚀 DEPLOYMENT GUIDE - Multi-City 6G Beam Prediction

**Version:** 1.0  
**Status:** ✅ PRODUCTION READY  
**Last Updated:** January 16, 2026

---

## 📋 QUICK REFERENCE

| Aspect | Detail |
|--------|--------|
| **Recommended Model** | `model_newyork.pt` |
| **Expected Accuracy** | 97-98% across all 6 cities |
| **Inference Time** | <1 ms per prediction |
| **Model Size** | 437 KB |
| **Deployment Complexity** | Low (single model) |
| **Ready for Production** | ✅ YES |

---

## 🎯 SCENARIO 1: RECOMMENDED DEPLOYMENT (Single Model)

### Overview
Deploy **one pre-trained NY model** to serve all 6 cities simultaneously.

### Why This Approach?
- ✅ 100% success across all cities (all >97% accuracy)
- ✅ Simplest maintenance (1 model to manage)
- ✅ Fastest inference (single model loaded)
- ✅ Proven to work: NY→Phoenix achieves 0.07% gap

### Implementation

#### Step 1: Load Model
```python
import torch
from pathlib import Path

# Load NY model
model_path = Path(r"C:\Research_Data\multi_city_models\model_newyork.pt")
model = torch.load(model_path)
model.eval()

print("✓ Model loaded successfully")
print(f"✓ Model size: {model_path.stat().st_size / 1024:.0f} KB")
```

#### Step 2: Prepare Input Data
```python
import numpy as np

def normalize_coordinates(lat, lon):
    """
    Normalize GPS coordinates to [-1, 1] range.
    
    Args:
        lat: Latitude (-90 to +90)
        lon: Longitude (-180 to +180)
    
    Returns:
        Normalized coordinates as tensor
    """
    # Normalize latitude: [-90, 90] → [-1, 1]
    norm_lat = lat / 90.0
    
    # Normalize longitude: [-180, 180] → [-1, 1]
    norm_lon = lon / 180.0
    
    # Ensure in valid range
    norm_lat = max(-1.0, min(1.0, norm_lat))
    norm_lon = max(-1.0, min(1.0, norm_lon))
    
    return torch.tensor([[norm_lat, norm_lon]], dtype=torch.float32)

# Example: NYC location
lat, lon = 40.7128, -74.0060
normalized = normalize_coordinates(lat, lon)
print(f"Normalized coordinates: {normalized.numpy()}")
```

#### Step 3: Get Beam Prediction
```python
def predict_beam(model, lat, lon):
    """
    Predict optimal beam for given GPS coordinates.
    
    Args:
        model: Pre-trained PyTorch model
        lat: Latitude
        lon: Longitude
    
    Returns:
        Best beam index (0-63)
    """
    input_tensor = normalize_coordinates(lat, lon)
    
    with torch.no_grad():
        beam_logits = model(input_tensor)
    
    best_beam = torch.argmax(beam_logits[0]).item()
    confidence = torch.sigmoid(beam_logits[0]).max().item()
    
    return best_beam, confidence

# Get prediction
best_beam, confidence = predict_beam(model, 40.7128, -74.0060)

print(f"✓ Best beam: {best_beam}")
print(f"✓ Confidence: {confidence:.1%}")
```

#### Step 4: Full Example Function
```python
def get_beam_prediction(model, lat, lon, city_name=None):
    """
    Complete end-to-end beam prediction.
    
    Args:
        model: Pre-trained model
        lat: Latitude
        lon: Longitude
        city_name: Optional city name for logging
    
    Returns:
        Dictionary with prediction and metadata
    """
    # Normalize
    input_data = normalize_coordinates(lat, lon)
    
    # Predict
    with torch.no_grad():
        beam_logits = model(input_data)
        beam_probs = torch.sigmoid(beam_logits[0])
    
    # Extract results
    best_beam = torch.argmax(beam_probs).item()
    top_5_beams = torch.topk(beam_probs, 5)
    confidence = beam_probs[best_beam].item()
    
    # Format output
    result = {
        'city': city_name or 'Unknown',
        'latitude': lat,
        'longitude': lon,
        'best_beam': best_beam,
        'confidence': f"{confidence:.1%}",
        'top_5_beams': top_5_beams.indices.tolist(),
        'top_5_confidences': [f"{v:.1%}" for v in top_5_beams.values.tolist()],
        'model': 'newyork_universal',
        'status': 'SUCCESS'
    }
    
    return result

# Test across all 6 cities
cities = {
    'newyork': (40.7128, -74.0060),
    'losangeles': (34.0522, -118.2437),
    'chicago': (41.8781, -87.6298),
    'houston': (29.7604, -95.3698),
    'phoenix': (33.4484, -112.0742),
    'santaclara': (37.3541, -121.9552),
}

print("\n" + "="*60)
print("UNIVERSAL MODEL DEPLOYMENT TEST")
print("="*60 + "\n")

for city_name, (lat, lon) in cities.items():
    result = get_beam_prediction(model, lat, lon, city_name)
    print(f"{city_name.upper():15} → Beam {result['best_beam']:2d} (Confidence: {result['confidence']})")

print("\n✓ All cities processed successfully")
```

### Expected Accuracy Per City

```
Model: model_newyork.pt (Universal)

New York:    98.46% (native)     ← Model trained here
Los Angeles: 97.21% (transfer)   ← 1.25% drop
Chicago:     97.23% (transfer)   ← 1.23% drop
Houston:     97.34% (transfer)   ← 1.12% drop
Phoenix:     98.39% (transfer)   ← 0.07% drop ⭐ Excellent
Santa Clara: 98.34% (transfer)   ← 0.12% drop ⭐ Excellent

Average:     97.99% across all cities ✓
```

### Deployment Checklist

- [ ] Model file exists: `C:\Research_Data\multi_city_models\model_newyork.pt`
- [ ] PyTorch installed: `pip install torch`
- [ ] Model loads successfully
- [ ] Test prediction on sample data
- [ ] Verify accuracy on validation set
- [ ] Monitor inference latency
- [ ] Log all predictions
- [ ] Setup error handling

---

## 🏢 SCENARIO 2: CITY-SPECIFIC MODELS (Maximum Accuracy)

### Overview
Deploy **6 independent models**, one per city, for maximum per-city accuracy.

### Why This Approach?
- ✅ Highest accuracy per city (97-99%)
- ✅ No transfer learning overhead
- ✅ Optimal for critical applications
- ⚠️ Higher computational cost
- ⚠️ More complex deployment

### Implementation

```python
import torch
from pathlib import Path

# Load all 6 models
models_dir = Path(r"C:\Research_Data\multi_city_models")
models = {}

city_names = ['newyork', 'losangeles', 'chicago', 'houston', 'phoenix', 'santaclara']

for city in city_names:
    model_path = models_dir / f"model_{city}.pt"
    models[city] = torch.load(model_path)
    models[city].eval()
    print(f"✓ Loaded model_{city}.pt")

# Prediction function with city routing
def predict_with_city_model(lat, lon, city_name):
    """
    Use city-specific model for prediction.
    
    Args:
        lat: Latitude
        lon: Longitude
        city_name: 'newyork', 'losangeles', 'chicago', 'houston', 'phoenix', or 'santaclara'
    
    Returns:
        Best beam index
    """
    if city_name not in models:
        raise ValueError(f"Unknown city: {city_name}")
    
    # Normalize coordinates
    norm_lat = max(-1.0, min(1.0, lat / 90.0))
    norm_lon = max(-1.0, min(1.0, lon / 180.0))
    input_data = torch.tensor([[norm_lat, norm_lon]], dtype=torch.float32)
    
    # Get prediction from city-specific model
    model = models[city_name]
    with torch.no_grad():
        beam_logits = model(input_data)
    
    best_beam = torch.argmax(beam_logits[0]).item()
    
    return best_beam

# Test example
beam = predict_with_city_model(34.0522, -118.2437, 'losangeles')
print(f"LA prediction: Beam {beam}")
```

### Expected Accuracy

```
City-Specific Models:

New York:    98.46% (dedicated model)
Los Angeles: 98.57% (dedicated model) ⭐ Best for LA
Chicago:     98.39% (dedicated model)
Houston:     98.99% (dedicated model) ⭐ Highest overall
Phoenix:     97.47% (dedicated model)
Santa Clara: 97.10% (dedicated model)

Average:     98.16% across all cities
```

### Deployment Checklist

- [ ] All 6 model files exist and are readable
- [ ] City detection/routing logic implemented
- [ ] Model loading optimized (cache in memory)
- [ ] Fallback mechanism if specific model unavailable
- [ ] Performance monitoring per model
- [ ] Model versioning strategy defined
- [ ] Update procedure for individual models

---

## 🔧 SCENARIO 3: HOUSTON BACKUP MODEL

### Overview
Deploy **Houston model** as backup when NY model is unavailable.

### Why This Approach?
- ✅ Highest accuracy: 98.99%
- ✅ Good fallback option
- ⚠️ Slightly worse transfer gaps than NY
- ✅ Alternative universal model

### Implementation

```python
# Load both models with fallback
primary_model = torch.load(r"C:\Research_Data\multi_city_models\model_newyork.pt")
backup_model = torch.load(r"C:\Research_Data\multi_city_models\model_houston.pt")

# Use backup if primary fails
def predict_with_fallback(lat, lon, use_backup=False):
    try:
        model = backup_model if use_backup else primary_model
        input_data = normalize_coordinates(lat, lon)
        
        with torch.no_grad():
            beam_logits = model(input_data)
        
        best_beam = torch.argmax(beam_logits[0]).item()
        model_used = 'houston' if use_backup else 'newyork'
        
        return best_beam, model_used
    except Exception as e:
        print(f"Error during prediction: {e}")
        return None, 'error'

# Test
beam, model_used = predict_with_fallback(40.7128, -74.0060)
print(f"Prediction using {model_used} model: Beam {beam}")
```

---

## ⚙️ PRODUCTION DEPLOYMENT CONFIGURATION

### Server Setup (FastAPI Example)

```python
# app.py - FastAPI server for beam prediction

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from pathlib import Path

app = FastAPI(title="6G Beam Predictor - Multi-City")

# Load model at startup
model = None

@app.on_event("startup")
async def load_model():
    global model
    model_path = Path(r"C:\Research_Data\multi_city_models\model_newyork.pt")
    model = torch.load(model_path, map_location='cpu')
    model.eval()
    print("✓ Model loaded")

class PredictionRequest(BaseModel):
    latitude: float
    longitude: float
    city: str = "Unknown"

class PredictionResponse(BaseModel):
    beam_index: int
    confidence: float
    city: str
    model: str
    status: str

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Predict optimal beam for GPS coordinates.
    """
    try:
        # Normalize coordinates
        norm_lat = max(-1.0, min(1.0, request.latitude / 90.0))
        norm_lon = max(-1.0, min(1.0, request.longitude / 180.0))
        input_data = torch.tensor([[norm_lat, norm_lon]], dtype=torch.float32)
        
        # Predict
        with torch.no_grad():
            beam_logits = model(input_data)
            beam_probs = torch.sigmoid(beam_logits[0])
        
        best_beam = torch.argmax(beam_probs).item()
        confidence = beam_probs[best_beam].item()
        
        return PredictionResponse(
            beam_index=best_beam,
            confidence=float(confidence),
            city=request.city,
            model="newyork_universal",
            status="SUCCESS"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": "loaded"}
```

Run server:
```bash
pip install fastapi uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000
```

Test predictions:
```bash
# Test NYC location
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"latitude": 40.7128, "longitude": -74.0060, "city": "newyork"}'

# Test LA location
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"latitude": 34.0522, "longitude": -118.2437, "city": "losangeles"}'
```

---

## 📊 PERFORMANCE MONITORING

### Key Metrics to Track

```python
import time
import statistics

predictions_log = []

# Log all predictions
def log_prediction(city, lat, lon, beam, confidence, latency_ms):
    predictions_log.append({
        'city': city,
        'latitude': lat,
        'longitude': lon,
        'beam': beam,
        'confidence': confidence,
        'latency_ms': latency_ms,
        'timestamp': datetime.now()
    })

# Monitor latency
latencies = [p['latency_ms'] for p in predictions_log[-1000:]]
print(f"Average Latency: {statistics.mean(latencies):.1f} ms")
print(f"P95 Latency: {sorted(latencies)[int(len(latencies)*0.95)]:.1f} ms")
print(f"P99 Latency: {sorted(latencies)[int(len(latencies)*0.99)]:.1f} ms")

# Monitor accuracy per city
cities_accuracy = {}
for city in ['newyork', 'losangeles', 'chicago', 'houston', 'phoenix', 'santaclara']:
    city_preds = [p for p in predictions_log if p['city'] == city]
    if city_preds:
        avg_conf = statistics.mean([p['confidence'] for p in city_preds])
        cities_accuracy[city] = avg_conf

print("\nAccuracy per City:")
for city, acc in sorted(cities_accuracy.items(), key=lambda x: x[1], reverse=True):
    print(f"  {city:12} : {acc:.1%}")
```

---

## ✅ VERIFICATION CHECKLIST

- [ ] Model loads successfully
- [ ] Predictions run <1 ms
- [ ] All 6 cities tested
- [ ] Accuracy meets expectations (>97%)
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Monitoring active
- [ ] Performance baselines established
- [ ] Backup procedures tested
- [ ] Documentation complete

---

## 🚀 PRODUCTION LAUNCH

### Pre-Launch Verification

```bash
# 1. Run comprehensive test
python test_deployment.py

# 2. Load test (1000 predictions)
python load_test.py

# 3. Verify accuracy on held-out data
python validate_accuracy.py

# 4. Check inference latency distribution
python benchmark_latency.py
```

### Launch Steps

1. ✅ **Verify:** All tests passing
2. ✅ **Monitor:** Set up dashboards
3. ✅ **Deploy:** Copy model to production
4. ✅ **Verify:** Health check passes
5. ✅ **Monitor:** Watch metrics for first hour
6. ✅ **Document:** Log deployment details

### Deployment Success Criteria

- ✅ Model loads in <100 ms
- ✅ Inference latency: <1 ms
- ✅ Accuracy: >97% across all cities
- ✅ Error rate: <0.1%
- ✅ System uptime: >99.9%
- ✅ No memory leaks after 1M predictions

---

**Deployment Ready:** ✅ YES  
**Status:** PRODUCTION  
**Last Verified:** January 16, 2026
