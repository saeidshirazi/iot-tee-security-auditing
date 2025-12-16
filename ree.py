#!/usr/bin/env python3
"""
ree.py
-------
Simulated IoT device in the normal world (REE).
Generates:
  - Physical state transitions
  - Possibly spoofed reported states
  - Random network connection attempts (TLS and non-TLS)
"""

import json
import random
import sys
import time


SECURE_ENDPOINTS = [
    "https://api.secure-server.com/upload",
    "mqtts://broker.secure.net/data",
    "wss://stream.iotcloud.com/feed"
]

INSECURE_ENDPOINTS = [
    "http://api.insecure-server.com/data",
    "mqtt://broker.local/publish",
    "ws://stream.local/feed"
]


def update_physical_state(current):
    if random.random() < 0.25:
        return "camera_on" if current == "camera_off" else "camera_off"
    return current


def generate_reported_state(actual):
    if actual == "camera_on" and random.random() < 0.40:
        return "camera_off", True
    return actual, False


def generate_network_attempt():
    """Simulate both secure and insecure outbound traffic."""
    if random.random() < 0.5:
        return random.choice(INSECURE_ENDPOINTS)
    return random.choice(SECURE_ENDPOINTS)


def main():
    print("[REE] Device simulator running...", file=sys.stderr)
    event_id = 0
    physical_state = "camera_off"

    try:
        while True:
            time.sleep(1.0)
            event_id += 1

            physical_state = update_physical_state(physical_state)
            reported_state, spoof = generate_reported_state(physical_state)
            connection = generate_network_attempt()

            event = {
                "event_id": event_id,
                "timestamp": time.time(),
                "device": "camera_1",
                "actual_state": physical_state,
                "reported_state": reported_state,
                "network_attempt": connection,
                "spoof_attempt": spoof
            }

            print(json.dumps(event), flush=True)

            dbg = f"[REE] event={event_id:03d} actual={physical_state} reported={reported_state} conn={connection}"
            if spoof:
                dbg += "  (spoofing)"
            print(dbg, file=sys.stderr)

    except KeyboardInterrupt:
        print("\n[REE] Stopped.", file=sys.stderr)


if __name__ == "__main__":
    main()
