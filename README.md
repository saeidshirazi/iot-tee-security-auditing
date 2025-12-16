# 🛡️ IoT Security Auditing with TEE & Provenance Visualization

A practical, end-to-end prototype demonstrating **TEE-based security auditing for IoT devices**, enhanced with **provenance analysis** and an **interactive security dashboard**.

This project simulates how a **Trusted Execution Environment (TEE)** can audit and enforce security policies on potentially compromised IoT devices, while providing explainable and visual security insights.

---

## 📌 Project Highlights

- 🔐 **TEE-style secure auditing**
- 🕵️ **Spoofing detection**
- 🫥 **Masking attack detection**
- 🔒 **TLS compliance enforcement**
- 🧾 **Trusted audit log generation**
- 🔗 **Provenance graph (cause → effect)**
- 📊 **Interactive dashboard**
  - multi-alert color badges
  - filtering by alert type
  - pagination for large event sets

---

## 🧠 Threat Model

This prototype assumes:
- The IoT device firmware (**REE – Normal World**) may be compromised
- An attacker can:
  - lie about device state (spoofing)
  - hide state transitions (masking)
  - use insecure network protocols
- The **TEE (Secure World)** is trusted and isolated

---

## 🏗️ Architecture Overview

```
┌──────────────┐
│   REE        │  Normal World (untrusted IoT device)
│  Device App  │
└──────┬───────┘
       │ JSON events
       ▼
┌──────────────────┐n│   TEE Auditor    │  Secure World (trusted)
│ - Spoofing check │
│ - Masking check  │
│ - TLS compliance │
│ - Secure logging │
└──────┬───────────┘
       ▼
┌─────────────────────────────┐
│ Dashboard + Provenance View │
│ - Interactive graph         │
│ - Filters & pagination      │
│ - Security insights         │
└─────────────────────────────┘
```

---

## ⚙️ Components

### `ree.py` — Normal World (IoT Device Simulation)
Simulates an IoT device that:
- Generates physical state changes (`camera_on / camera_off`)
- Reports device state (may be spoofed)
- Attempts network connections (secure & insecure)

The REE is intentionally allowed to misbehave.

---

### `tee.py` — Secure World (TEE Auditor)
Acts as a trusted auditor that:
- Detects **spoofing**  
  → reported state ≠ physical state
- Detects **masking attacks**  
  → physical state changes but reported state does not
- Enforces **TLS compliance**
- Writes **trusted audit logs** (`audit_log.jsonl`)

The REE cannot tamper with TEE logic or logs.

---

### `dashboard.py` — Analysis & Visualization
Parses the trusted audit logs and generates:
- Summary statistics
- Multi-alert event table
- Interactive provenance graph
- Filterable, paginated dashboard

Output:
```
dashboard.html
```

---

## 🚀 How to Run

### 1️⃣ Install dependencies
```bash
pipenv install
pipenv shell
```

### 2️⃣ Run the REE → TEE pipeline
```bash
python ree.py | python tee.py
```

Let it run for ~30 seconds, then stop with `Ctrl+C`.

### 3️⃣ Generate the dashboard
```bash
python dashboard.py
```

### 4️⃣ Open the dashboard
```bash
open dashboard.html        # macOS
xdg-open dashboard.html   # Linux
```

---

## 📊 Dashboard Features

- ✔ Summary cards (OK, spoofing, masking, TLS violations)
- ✔ Multi-color alert badges per event
- ✔ Alert-based filtering
- ✔ Pagination for large datasets
- ✔ Interactive provenance graph
- ✔ Clear visual explanation of attack causes

---

## 🔍 Understanding Alerts

| Alert Type | Meaning |
|-----------|--------|
| **Spoofing** | Device lies about its current state |
| **Masking** | Device hides physical state transitions |
| **TLS Violation** | Insecure network protocol used |
| **OK** | No policy violations |

Example:
```
Event 20 → [ SPOOFING ] [ TLS_VIOLATION ]
```

---

## 🔗 Provenance Graph: Why It Matters

The provenance graph connects:
- Event
- Physical state
- Reported state
- Network behavior
- Triggered alerts

This provides:
- Root-cause analysis
- Multi-stage attack visibility
- Explainable security alerts
- Strong forensic value

---

## 🔐 Comparison to Real TEEs

| This Prototype | Real TEE (ARM TrustZone / OP-TEE) |
|---------------|-----------------------------------|
| Python processes | Secure & Normal Worlds |
| Pipe (`|`) | Secure Monitor Calls (SMC) |
| JSON events | Shared memory |
| Audit log file | Secure storage (RPMB) |
| Policy logic | Trusted Application |

This project focuses on **logical correctness and security insight**, not hardware isolation.

---

## 📈 Future Work

- Cryptographic signing of audit logs
- Remote attestation
- Secure boot & firmware integrity
- Multi-device correlation
- Cloud-side compliance verification
- Deployment on real ARM TrustZone hardware

---

## 📜 License

MIT License (or update as needed).

---

## 🙌 Acknowledgements

Inspired by research on:
- Trusted Execution Environments
- IoT security compliance
- Provenance-based system auditing
- It is just a prototype

## 🙌 InfoSecTube 
Developed By Saeid Shirazi
