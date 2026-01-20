# AI Inference Service Integration

## Overview

This document explains how to integrate your YOLO model with the Django backend.

## Expected AI Service Response Format

The backend expects the AI inference service to return JSON in this format:

```json
{
    "status": "success",
    "detections": [
        {
            "class": "tiger",
            "confidence": 0.92,
            "bounding_boxes": [
                {
                    "x": 120,
                    "y": 200,
                    "width": 180,
                    "height": 240,
                    "confidence": 0.92
                }
            ]
        },
        {
            "class": "human",
            "confidence": 0.87,
            "bounding_boxes": [
                {
                    "x": 50,
                    "y": 100,
                    "width": 90,
                    "height": 150,
                    "confidence": 0.87
                }
            ]
        }
    ],
    "processing_time": 0.234
}
```

## Supported Animal Classes

```python
ANIMAL_CLASSES = [
    'tiger', 'lion', 'leopard', 'elephant', 'bear',
    'bison', 'boar', 'deer', 'human', 'other'
]
```

## Integration with Your YOLO Model

Based on your `model/train.py`, here's how to create an inference service:

### Option 1: FastAPI Service (Recommended)

Create `model/inference_service.py`:

```python
from fastapi import FastAPI, File, UploadFile
from ultralytics import YOLO
import numpy as np
from PIL import Image
import io
import time

app = FastAPI()

# Load your trained model
model = YOLO('runs/detect/50-epochs/weights/best.pt')

# Class mapping from your data.yaml
CLASS_NAMES = {
    0: 'bear',
    1: 'bison',
    2: 'boar',
    3: 'elephant',
    4: 'human',
    5: 'leopard',
    6: 'lion',
    7: 'tiger'
}

@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    start_time = time.time()
    
    try:
        # Read image
        image_data = await image.read()
        img = Image.open(io.BytesIO(image_data))
        
        # Run inference
        results = model(img)
        
        # Parse results
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                xyxy = box.xyxy[0].tolist()
                
                detection = {
                    "class": CLASS_NAMES.get(cls, "other"),
                    "confidence": conf,
                    "bounding_boxes": [{
                        "x": int(xyxy[0]),
                        "y": int(xyxy[1]),
                        "width": int(xyxy[2] - xyxy[0]),
                        "height": int(xyxy[3] - xyxy[1]),
                        "confidence": conf
                    }]
                }
                detections.append(detection)
        
        processing_time = time.time() - start_time
        
        return {
            "status": "success",
            "detections": detections,
            "processing_time": processing_time
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "detections": []
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Install FastAPI Dependencies

```bash
pip install fastapi uvicorn python-multipart
```

### Run the Inference Service

```bash
cd model/
python inference_service.py
```

The service will be available at `http://localhost:8001`

### Update Django Settings

In your `.env`:

```bash
AI_INFERENCE_URL=http://localhost:8001/predict
AI_INFERENCE_TIMEOUT=30
```

## Option 2: Direct Integration (Alternative)

If you want to run inference directly in Django without a separate service:

### Install YOLO in Django Environment

```bash
pip install ultralytics
```

### Update `api/tasks.py`

Replace the AI service HTTP call with direct inference:

```python
from ultralytics import YOLO
from PIL import Image

# Load model once at startup
AI_MODEL = YOLO('/path/to/your/best.pt')

@shared_task(bind=True, max_retries=3)
def process_image_with_ai(self, image_id):
    try:
        image = ImageCapture.objects.get(id=image_id)
    except ImageCapture.DoesNotExist:
        logger.error(f"Image {image_id} not found")
        return
    
    # Mark as processing started
    image.processing_started_at = timezone.now()
    image.save(update_fields=['processing_started_at'])
    
    try:
        # Load image
        img = Image.open(image.image.path)
        
        # Run inference
        results = AI_MODEL(img)
        
        # Parse results (same as above)
        ai_results = {"detections": []}
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # ... parse boxes
        
        # Continue with existing detection creation logic
        # ...
    except Exception as e:
        logger.error(f"Error processing image {image_id}: {str(e)}")
        raise self.retry(exc=e, countdown=60)
```

## Testing the AI Service

### Test with cURL

```bash
curl -X POST "http://localhost:8001/predict" \
  -F "image=@test_image.jpg"
```

### Test with Python

```python
import requests

url = "http://localhost:8001/predict"
with open("test_image.jpg", "rb") as f:
    files = {"image": f}
    response = requests.post(url, files=files)
    print(response.json())
```

## Performance Optimization

### GPU Acceleration

If you have a GPU:

```python
# In inference service
model = YOLO('best.pt')
model.to('cuda')  # Use GPU
```

### Batch Processing

For multiple images:

```python
results = model(['img1.jpg', 'img2.jpg', 'img3.jpg'])
```

### Model Optimization

```python
# Export to ONNX for faster inference
model.export(format='onnx')
model = YOLO('best.onnx')
```

## Deployment

### Docker Container for AI Service

Create `model/Dockerfile`:

```dockerfile
FROM python:3.10

WORKDIR /app

# Install dependencies
RUN pip install ultralytics fastapi uvicorn python-multipart

# Copy model and code
COPY best.pt /app/
COPY inference_service.py /app/

# Expose port
EXPOSE 8001

# Run service
CMD ["python", "inference_service.py"]
```

Build and run:

```bash
docker build -t animal-ai-service .
docker run -p 8001:8001 animal-ai-service
```

## Monitoring AI Service

Add health check endpoint:

```python
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }
```

Check:
```bash
curl http://localhost:8001/health
```

## Troubleshooting

### Model Not Loading

```bash
# Check model path
ls -lh runs/detect/50-epochs/weights/best.pt

# Test loading
python -c "from ultralytics import YOLO; m = YOLO('best.pt'); print('OK')"
```

### Low Confidence Scores

Adjust confidence threshold in Django settings:

```python
RISK_LEVELS = {
    "LOW": {
        "confidence_threshold": 0.4,  # Lower threshold
        # ...
    }
}
```

### Slow Inference

- Use GPU if available
- Reduce image size before inference
- Use lighter model (yolo11n.pt instead of yolo11l.pt)
- Export to ONNX or TensorRT

---

This integration allows your trained YOLO model to work seamlessly with the Django backend!
