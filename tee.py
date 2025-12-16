#!/usr/bin/env python3
"""
tee.py
-------
Secure-world auditor simulator.

Detects:
  - Spoofing attacks
  - Masking attacks
  - TLS compliance violations
Logs audit records to audit_log.jsonl
"""

import json
import sys
import time

AUDIT_LOG = "audit_log.jsonl"

last_physical = None
last_reported = None


def detect_spoofing(actual, reported):
    return actual != reported


def detect_masking(actual, reported):
    global last_physical, last_reported

    if last_physical is None:
        last_physical = actual
        last_reported = reported
        return False

    physical_changed = actual != last_physical
    reported_changed = reported != last_reported

    last_physical = actual
    last_reported = reported

    return physical_changed and not reported_changed


def tls_violation(url):
    url = url.lower()
    insecure_prefixes = ("http://", "mqtt://", "ws://")
    return url.startswith(insecure_prefixes)


def main():
    print("[TEE] Auditor running...", file=sys.stderr)

    try:
        with open(AUDIT_LOG, "a", buffering=1) as logf:
            for line in sys.stdin:
                if not line.strip():
                    continue

                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    print("[TEE] Invalid JSON.", file=sys.stderr)
                    continue

                actual = event["actual_state"]
                reported = event["reported_state"]
                connection = event["network_attempt"]

                alerts = []

                if detect_spoofing(actual, reported):
                    alerts.append("spoofing")

                if detect_masking(actual, reported):
                    alerts.append("masking")

                if tls_violation(connection):
                    alerts.append("tls_violation")

                record = {
                    "time_tee": time.time(),
                    "event_id": event["event_id"],
                    "device": event["device"],
                    "actual_state": actual,
                    "reported_state": reported,
                    "network_attempt": connection,
                    "alerts": alerts,
                }

                logf.write(json.dumps(record) + "\n")

                status = "OK" if not alerts else ", ".join(alerts)
                print(
                    f"[TEE] event={event['event_id']:03d} actual={actual:<11} "
                    f"reported={reported:<11} conn={connection:<45} result={status}",
                    file=sys.stderr,
                )

    except KeyboardInterrupt:
        print("\n[TEE] Auditor stopped.", file=sys.stderr)


if __name__ == "__main__":
    main()
