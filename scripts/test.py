import json
import os
import sys

METRICS_FILE = '/app/metrics.json'

print("=" * 40)
print("UAV SIMULATION TEST REPORT")
print("=" * 40)

if not os.path.exists(METRICS_FILE):
    print("FAIL — metrics.json not found")
    print("Simulation did not complete or controller crashed")
    sys.exit(1)

with open(METRICS_FILE) as f:
    m = json.load(f)

target = m['target']
pos = m['final_position']

print(f"Target:         ({target['x']}, {target['y']}, {target['z']})")
print(f"Final position: ({pos['x']}, {pos['y']}, {pos['z']})")
print(f"Deviation:      {m['deviation_from_target_m']} m")
print(f"Flight time:    {m['flight_time_s']} s")
print("-" * 40)

if m['mission_success']:
    print("RESULT: PASS — target reached")
    sys.exit(0)
else:
    print("RESULT: FAIL — target not reached")
    sys.exit(1)
