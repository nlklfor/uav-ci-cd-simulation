import json
import sys
import time
from pathlib import Path

import ultralytics
from ultralytics import YOLO

CONFIDENCE_THRESHOLD = 0.5
LATENCY_THRESHOLD_MS = 5000
RESULTS_FILE = 'perception_results.json'


def main():
    test_image = str(Path(ultralytics.__file__).parent / 'assets' / 'bus.jpg')

    print("Loading YOLOv8n model...")
    model = YOLO('yolov8n.pt')

    print(f"Running inference on test image: {test_image}")
    t0 = time.time()
    results = model(test_image, verbose=False)
    latency_ms = (time.time() - t0) * 1000

    detections = [
        {
            'class': model.names[int(box.cls[0])],
            'confidence': round(float(box.conf[0]), 3),
        }
        for result in results
        for box in result.boxes
    ]

    max_confidence = max((d['confidence'] for d in detections), default=0.0)
    detected_classes = sorted(set(d['class'] for d in detections))

    passed = (
        len(detections) > 0
        and max_confidence >= CONFIDENCE_THRESHOLD
        and latency_ms < LATENCY_THRESHOLD_MS
    )

    output = {
        'test_passed': passed,
        'model': 'yolov8n',
        'detections_count': len(detections),
        'max_confidence': round(max_confidence, 3),
        'inference_latency_ms': round(latency_ms, 1),
        'detected_classes': detected_classes,
        'thresholds': {
            'min_confidence': CONFIDENCE_THRESHOLD,
            'max_latency_ms': LATENCY_THRESHOLD_MS,
        },
    }

    with open(RESULTS_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print("=" * 40)
    print("YOLO PERCEPTION TEST REPORT")
    print("=" * 40)
    print(f"Model:       {output['model']}")
    print(f"Detections:  {output['detections_count']}")
    print(f"Confidence:  {output['max_confidence']}")
    print(f"Latency:     {output['inference_latency_ms']} ms")
    print(f"Classes:     {detected_classes}")
    print("=" * 40)
    print(f"RESULT: {'PASS' if passed else 'FAIL'}")
    print("=" * 40)

    return 0 if passed else 1


if __name__ == '__main__':
    sys.exit(main())
