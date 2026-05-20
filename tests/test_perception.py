import json
import os
import sys
import time
from pathlib import Path

import ultralytics
from ultralytics import YOLO

CONFIDENCE_THRESHOLD = 0.5
LATENCY_THRESHOLD_MS = 5000
RESULTS_FILE = 'perception_results.json'


def run_inference(model, image_path):
    t0 = time.time()
    results = model(image_path, verbose=False)
    latency_ms = (time.time() - t0) * 1000
    detections = [
        {
            'class': model.names[int(box.cls[0])],
            'confidence': round(float(box.conf[0]), 3),
        }
        for result in results
        for box in result.boxes
    ]
    return detections, round(latency_ms, 1)


def main():
    # Primary test image: aerial drone view committed to repo
    aerial_image = str(Path(__file__).parent / 'aerial_test.jpg')
    fallback_image = str(Path(ultralytics.__file__).parent / 'assets' / 'bus.jpg')

    test_image = aerial_image if os.path.exists(aerial_image) else fallback_image
    print(f"Using test image: {test_image}")

    print("Loading YOLOv8n model...")
    model = YOLO('yolov8n.pt')

    detections, latency_ms = run_inference(model, test_image)
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
        'test_image': os.path.basename(test_image),
        'detections_count': len(detections),
        'max_confidence': round(max_confidence, 3),
        'inference_latency_ms': latency_ms,
        'detected_classes': detected_classes,
        'thresholds': {
            'min_confidence': CONFIDENCE_THRESHOLD,
            'max_latency_ms': LATENCY_THRESHOLD_MS,
        },
    }

    # Also analyse simulation camera frame if available (informational only)
    scene_capture = 'scene_capture.jpg'
    if os.path.exists(scene_capture):
        scene_dets, scene_lat = run_inference(model, scene_capture)
        output['scene_capture'] = {
            'detections_count': len(scene_dets),
            'detected_classes': sorted(set(d['class'] for d in scene_dets)),
            'inference_latency_ms': scene_lat,
        }
        print(f"Scene capture: {len(scene_dets)} detections "
              f"({', '.join(output['scene_capture']['detected_classes']) or 'none'})")

    with open(RESULTS_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print("=" * 40)
    print("YOLO PERCEPTION TEST REPORT")
    print("=" * 40)
    print(f"Model:       {output['model']}")
    print(f"Test image:  {output['test_image']}")
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
