import time
import random

print("Starting UAV simulation test...")
time.sleep(2)

collision = random.choice([True, False])

if collision:
    print("FAIL - Collision detected")
    exit(1)
else:
    print("SUCCESS - No collision")
    exit(0)
    
