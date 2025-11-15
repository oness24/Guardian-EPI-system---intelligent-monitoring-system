# Implementation Guide
## Guardian EPI - Developer's Guide

This guide provides practical implementation details for developers working with the Guardian EPI system.

---

## Quick Start for Developers

### 1. Clone and Setup

```bash
# Clone repository
git clone https://github.com/yourusername/guardian-epi.git
cd guardian-epi

# Create virtual environment with Python 3.10
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
python test_system.py
```

Expected output:
```
✅ NumPy: 1.26.4
✅ OpenCV: 4.11.0
✅ TensorFlow: 2.15.1
✅ Pillow: 11.0.0
✅ Model loaded successfully
✅ Input shape: (None, 224, 224, 3)
✅ Output shape: (None, 2)
```

### 3. Run Tests

```bash
# Full test suite with 40 images
python run_test_images.py

# Single image demo
python demo_single_image.py test_images/epi/com_epi/1000.jpg
```

---

## Core Components

### MonitorEPI Class

The main monitoring system is implemented in `monitor_epi.py`. Here's how to use it:

```python
from monitor_epi import MonitorEPI

# Initialize monitor
monitor = MonitorEPI()

# Process an image file
class_name, confidence = monitor.process_image_file('path/to/image.jpg')

# Process from webcam
monitor.process_camera(camera_index=0)
```

### Key Methods

#### Image Preprocessing

```python
def preprocess_image(self, image):
    """
    Prepares image for model inference.

    Args:
        image: PIL Image or NumPy array

    Returns:
        np.ndarray: Preprocessed image array (1, 224, 224, 3)
    """
    # Resize to 224x224
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)

    image = image.resize((224, 224), Image.LANCZOS)

    # Convert to array and normalize
    image_array = np.asarray(image, dtype=np.float32)
    normalized = image_array / 255.0

    # Add batch dimension
    return np.expand_dims(normalized, axis=0)
```

#### Prediction

```python
def predict(self, image):
    """
    Performs prediction on preprocessed image.

    Args:
        image: PIL Image or NumPy array

    Returns:
        tuple: (class_name, confidence)
            - class_name (str): 'com_EPI' or 'sem_EPI'
            - confidence (float): Prediction confidence [0.0, 1.0]
    """
    processed_image = self.preprocess_image(image)
    predictions = self.model.predict(processed_image, verbose=0)

    class_index = np.argmax(predictions[0])
    confidence = predictions[0][class_index]
    class_name = self.labels[class_index]

    return class_name, confidence
```

---

## Use Case Implementations

### 1. PPE Monitoring (`monitor_epi.py`)

**Purpose**: Monitor PPE compliance at factory entrance

**Key Features**:
- Real-time camera monitoring
- Access control integration ready
- Email alerts on violations
- Comprehensive logging

**Usage Example**:

```python
from monitor_epi import MonitorEPI

monitor = MonitorEPI()

# For entry gate monitoring
def check_worker_entry(camera_feed):
    class_name, confidence = monitor.predict(camera_feed)

    if class_name == 'com_EPI' and confidence >= 0.70:
        print("✅ Access GRANTED - PPE detected")
        return True
    else:
        print("❌ Access DENIED - PPE missing")
        monitor.trigger_alert(camera_feed)
        return False
```

### 2. Uniform Compliance (`controle_uniforme.py`)

**Purpose**: Verify sterile uniform compliance in food processing areas

**Difference from PPE Monitor**:
- Higher threshold (75% vs 70%)
- Compliance reports in JSON format
- Focus on complete uniform (coat, hair net, beard cover)

**Usage Example**:

```python
from controle_uniforme import ControleUniforme

controller = ControleUniforme()

def verify_packaging_area_entry(worker_image):
    result = controller.verificar_conformidade(worker_image)

    if result['conforme']:
        print(f"✅ Uniform OK - Confidence: {result['confianca']:.1%}")
        return True
    else:
        print(f"❌ Non-compliant - Reason: {result['motivo']}")
        controller.registrar_nao_conformidade(worker_image)
        return False
```

### 3. Object Detection (`detector_objetos.py`)

**Purpose**: Detect prohibited objects in high-security areas

**Detected Objects**:
- Smartphones
- Cameras
- USB drives
- Recording devices
- Smartwatches

**Usage Example**:

```python
from detector_objetos import DetectorObjetos

detector = DetectorObjetos()

def security_screening(bag_image):
    detection = detector.analisar_objeto(bag_image)

    if detection['proibido']:
        print(f"⚠️ PROHIBITED: {detection['objeto']}")
        print(f"   Confidence: {detection['confianca']:.1%}")
        detector.registrar_incidente_seguranca(bag_image)
        return False
    else:
        print("✅ Clear - No prohibited items")
        return True
```

---

## Model Details

### Architecture

The system uses MobileNetV2 architecture with transfer learning:

```
Input: (224, 224, 3) RGB Image
         ↓
    MobileNetV2
    (Pre-trained)
         ↓
  GlobalAveragePooling2D
         ↓
    Dense (128, ReLU)
         ↓
     Dropout (0.5)
         ↓
  Dense (2, Softmax)
         ↓
Output: [P(com_EPI), P(sem_EPI)]
```

### Model Files

```
models/
├── keras_model.h5    # Main trained model (8.9 MB)
└── labels.txt        # Class labels
```

**labels.txt** format:
```
0 com_EPI
1 sem_EPI
```

### Loading Custom Models

To use a different model:

```python
monitor = MonitorEPI(
    model_path='path/to/your/model.h5',
    labels_path='path/to/your/labels.txt'
)
```

---

## Configuration

### Confidence Thresholds

Adjust confidence thresholds based on your use case:

```python
# In monitor_epi.py
CONFIDENCE_THRESHOLD = 0.70  # 70% - Balanced

# For higher security (fewer false negatives)
CONFIDENCE_THRESHOLD = 0.60  # 60% - More sensitive

# For fewer false alarms (fewer false positives)
CONFIDENCE_THRESHOLD = 0.85  # 85% - More strict
```

### Alert Configuration

Configure email alerts in the code:

```python
# Email settings (monitor_epi.py lines 50-55)
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'alerts@company.com',
    'sender_password': 'your_password',  # Use environment variable!
    'recipient_email': 'supervisor@company.com'
}
```

**Security Note**: Use environment variables for credentials:

```python
import os

EMAIL_CONFIG = {
    'sender_email': os.getenv('ALERT_EMAIL'),
    'sender_password': os.getenv('ALERT_PASSWORD'),
    'recipient_email': os.getenv('SUPERVISOR_EMAIL')
}
```

### Logging Configuration

Logs are stored in `logs/` directory:

```python
LOG_DIR = 'logs'
ALERT_IMAGE_DIR = 'logs/alerts'

# Log rotation (optional)
MAX_LOG_SIZE_MB = 100
LOG_RETENTION_DAYS = 30
```

---

## Camera Integration

### OpenCV Camera

Basic webcam integration:

```python
import cv2

def monitor_from_camera(monitor, camera_index=0):
    cap = cv2.VideoCapture(camera_index)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Predict
        class_name, confidence = monitor.predict(rgb_frame)

        # Display
        color = (0, 255, 0) if class_name == 'com_EPI' else (0, 0, 255)
        text = f"{class_name}: {confidence:.1%}"
        cv2.putText(frame, text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        cv2.imshow('Guardian EPI', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
```

### IP Camera Integration

For RTSP streams:

```python
def monitor_from_ip_camera(monitor, rtsp_url):
    cap = cv2.VideoCapture(rtsp_url)

    # Example RTSP URL:
    # rtsp://username:password@192.168.1.64:554/stream
    # rtsp://192.168.1.100:8554/live

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Connection lost, reconnecting...")
            cap.release()
            cap = cv2.VideoCapture(rtsp_url)
            continue

        # Process frame
        class_name, confidence = monitor.predict(frame)

        # Your logic here
        if class_name == 'sem_EPI':
            monitor.trigger_alert(frame)

    cap.release()
```

---

## Performance Optimization

### GPU Acceleration

To use GPU for faster inference:

```bash
# Install CUDA-enabled TensorFlow
pip uninstall tensorflow
pip install tensorflow-gpu==2.15.1
```

Verify GPU usage:

```python
import tensorflow as tf

print("GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
```

### Model Quantization

For embedded devices (Raspberry Pi, Jetson Nano):

```python
import tensorflow as tf

# Load model
model = tf.keras.models.load_model('models/keras_model.h5')

# Convert to TFLite with quantization
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# Save quantized model
with open('models/model_quantized.tflite', 'wb') as f:
    f.write(tflite_model)
```

Use quantized model:

```python
import tensorflow as tf

# Load TFLite model
interpreter = tf.lite.Interpreter(model_path='models/model_quantized.tflite')
interpreter.allocate_tensors()

# Get input/output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Run inference
interpreter.set_tensor(input_details[0]['index'], preprocessed_image)
interpreter.invoke()
predictions = interpreter.get_tensor(output_details[0]['index'])
```

### Batch Processing

For processing multiple images efficiently:

```python
def predict_batch(monitor, image_paths, batch_size=32):
    """Process multiple images in batches."""
    results = []

    for i in range(0, len(image_paths), batch_size):
        batch_paths = image_paths[i:i+batch_size]
        batch_images = []

        # Load and preprocess batch
        for path in batch_paths:
            image = Image.open(path).convert('RGB')
            processed = monitor.preprocess_image(image)
            batch_images.append(processed[0])  # Remove batch dim

        # Stack into batch
        batch_array = np.stack(batch_images, axis=0)

        # Predict entire batch at once
        predictions = monitor.model.predict(batch_array, verbose=0)

        # Process results
        for j, pred in enumerate(predictions):
            class_idx = np.argmax(pred)
            confidence = pred[class_idx]
            class_name = monitor.labels[class_idx]
            results.append((batch_paths[j], class_name, confidence))

    return results
```

---

## Testing

### Unit Tests

Create `tests/test_monitor.py`:

```python
import unittest
from monitor_epi import MonitorEPI
from PIL import Image
import numpy as np

class TestMonitorEPI(unittest.TestCase):

    def setUp(self):
        self.monitor = MonitorEPI()

    def test_model_loads(self):
        """Test that model loads successfully."""
        self.assertIsNotNone(self.monitor.model)

    def test_labels_loaded(self):
        """Test that labels are loaded."""
        self.assertEqual(len(self.monitor.labels), 2)
        self.assertIn('com_EPI', self.monitor.labels)
        self.assertIn('sem_EPI', self.monitor.labels)

    def test_preprocessing_shape(self):
        """Test image preprocessing output shape."""
        image = Image.new('RGB', (640, 480))
        processed = self.monitor.preprocess_image(image)
        self.assertEqual(processed.shape, (1, 224, 224, 3))

    def test_prediction_output(self):
        """Test prediction returns correct format."""
        image = Image.new('RGB', (224, 224))
        class_name, confidence = self.monitor.predict(image)
        self.assertIsInstance(class_name, str)
        self.assertIsInstance(confidence, (float, np.floating))
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

if __name__ == '__main__':
    unittest.main()
```

Run tests:

```bash
python -m unittest tests/test_monitor.py
```

---

## Deployment Scenarios

### Scenario 1: Raspberry Pi Edge Device

```bash
# On Raspberry Pi 4 (4GB RAM)
sudo apt-get install python3-opencv python3-numpy
pip install tensorflow==2.15.1  # Or use TFLite

# Use quantized model for better performance
python monitor_epi.py --model models/model_quantized.tflite
```

### Scenario 2: Industrial PC with Multiple Cameras

```python
import multiprocessing

def monitor_camera(camera_id, monitor_instance):
    """Monitor single camera in separate process."""
    while True:
        # Monitoring logic
        pass

if __name__ == '__main__':
    # Create separate process for each camera
    cameras = [0, 1, 2, 3]  # 4 cameras
    processes = []

    for cam_id in cameras:
        monitor = MonitorEPI()
        p = multiprocessing.Process(
            target=monitor_camera,
            args=(cam_id, monitor)
        )
        p.start()
        processes.append(p)

    # Wait for all processes
    for p in processes:
        p.join()
```

### Scenario 3: Cloud-Based API Service

Using Flask:

```python
from flask import Flask, request, jsonify, send_file
from monitor_epi import MonitorEPI
import io

app = Flask(__name__)
monitor = MonitorEPI()

@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    """Analyze uploaded image."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    image = Image.open(file.stream)

    class_name, confidence = monitor.predict(image)

    return jsonify({
        'class': class_name,
        'confidence': float(confidence),
        'compliant': class_name == 'com_EPI' and confidence >= 0.70
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'model_loaded': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'tensorflow'`
```bash
# Solution: Ensure you're in virtual environment
source venv/bin/activate
pip install tensorflow==2.15.1
```

**Issue**: Low accuracy in production
```python
# Solution: Check image quality and lighting
def validate_image_quality(image):
    # Check brightness
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    brightness = np.mean(gray)
    if brightness < 50 or brightness > 200:
        print(f"⚠️ Warning: Poor lighting (brightness: {brightness})")

    # Check resolution
    if image.shape[0] < 480 or image.shape[1] < 640:
        print("⚠️ Warning: Low resolution")
```

**Issue**: Slow inference
```bash
# Check if using GPU
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"

# Consider model quantization or batch processing
```

---

## Best Practices

1. **Always validate image quality** before inference
2. **Use confidence thresholds** appropriate for your risk tolerance
3. **Log all decisions** for audit trail
4. **Test thoroughly** with diverse real-world scenarios
5. **Monitor performance** metrics in production
6. **Keep models updated** as conditions change
7. **Implement failsafe mechanisms** (manual override)
8. **Secure API endpoints** if deploying as service

---

## Contributing

To extend functionality:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/NewDetector`)
3. Add tests for new features
4. Ensure all tests pass
5. Submit pull request

---

## Additional Resources

- **TensorFlow Documentation**: https://www.tensorflow.org/api_docs
- **OpenCV Documentation**: https://docs.opencv.org/
- **MobileNet Paper**: https://arxiv.org/abs/1704.04861

---

**Version**: 1.0.0
**Last Updated**: November 2025
**Status**: Production Ready
