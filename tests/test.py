import sounddevice as sd
import json

print("\n=== AVAILABLE DEVICES ===")
print(json.dumps(sd.query_devices(), indent=2))

print("\n=== DEFAULT DEVICE ===")
print(sd.default.device)

#print("\n=== VB-Cable device index FOUND by code ===")
#print(device_index)
