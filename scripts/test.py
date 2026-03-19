import time
import random

print("Strating UAV simulation test...")
time.sleep(2)

collission = random.choice([True, False])

if collission:
    print("SUCCESS")
    exit(1)
else:
    print("FAIL")
    exit(0)
    
