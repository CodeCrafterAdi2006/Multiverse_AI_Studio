# Skill: Computer Vision - Object Detection

## Purpose
To locate and identify multiple objects within an image or video stream by drawing bounding boxes and assigning class labels with confidence scores.

## When to Use
- When counting objects (e.g., people in a crowd, cars on a road)
- When building autonomous navigation systems or robotics
- When performing automated quality inspection in manufacturing
- When extracting specific elements from documents (e.g., tables, signatures)

## Procedure

### 1. Choose the Architecture
Select an architecture based on the trade-off between speed and accuracy:
- **YOLO (You Only Look Once)**: Best for real-time inference (YOLOv8, YOLOv10). Very fast and highly accurate.
- **Faster R-CNN**: Slower but highly accurate, especially for small objects. Good for medical imaging.
- **DETR (DEtection TRansformer)**: Transformer-based approach that eliminates the need for non-maximum suppression (NMS) and anchor boxes.

### 2. Dataset Preparation
Ensure the dataset is properly formatted. The most common formats are:
- **COCO JSON**: A single JSON file containing images, annotations (bounding boxes, polygons), and categories.
- **YOLO TXT**: One text file per image containing `class_id x_center y_center width height` (normalized between 0 and 1).

**Data Augmentation**:
Apply augmentations to improve robustness using libraries like `albumentations`:
```python
import albumentations as A

transform = A.Compose([
    A.HorizontalFlip(p=0.5),
    A.RandomBrightnessContrast(p=0.2),
    A.ShiftScaleRotate(shift_limit=0.0625, scale_limit=0.1, rotate_limit=45, p=0.2),
], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))
```

### 3. YOLOv8 Implementation Example
Using the Ultralytics library for training and inference.

**Installation**:
```bash
pip install ultralytics
```

**Training**:
Create a `data.yaml` file defining the dataset paths and classes:
```yaml
train: ../train/images
val: ../valid/images

nc: 3 # number of classes
names: ['car', 'pedestrian', 'traffic_light']
```

```python
from ultralytics import YOLO

# Load a pre-trained model (recommended for transfer learning)
model = YOLO('yolov8n.pt') # 'n' for nano, 's' for small, 'm' for medium, etc.

# Train the model on your custom dataset
results = model.train(data='data.yaml', epochs=100, imgsz=640, batch=16, device=0)
```

**Inference**:
```python
from ultralytics import YOLO
import cv2

# Load the fine-tuned model
model = YOLO('runs/detect/train/weights/best.pt')

# Perform inference on an image
results = model('test_image.jpg')

# View results
for result in results:
    boxes = result.boxes  # Bounding boxes object
    for box in boxes:
        # Extract coordinates, confidence, and class id
        x1, y1, x2, y2 = box.xyxy[0]
        conf = box.conf[0]
        cls_id = int(box.cls[0])
        print(f"Class: {model.names[cls_id]}, Confidence: {conf:.2f}, Box: [{x1}, {y1}, {x2}, {y2}]")
```

### 4. Evaluation Metrics
Understand the standard metrics for object detection:
- **IoU (Intersection over Union)**: Measures the overlap between the predicted bounding box and the ground truth.
- **mAP (Mean Average Precision)**: The primary metric. Often calculated at different IoU thresholds (e.g., mAP@0.5, mAP@0.5:0.95).

## Best Practices
- Ensure a balanced dataset across all classes to prevent the model from ignoring rare objects.
- Pay attention to image size (`imgsz`). Larger sizes detect smaller objects better but require more memory and slow down inference.
- Utilize pre-trained weights (Transfer Learning) instead of training from scratch whenever possible.