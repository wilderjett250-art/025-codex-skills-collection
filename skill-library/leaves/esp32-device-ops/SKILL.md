---
name: esp32-device-ops
description: 'Identify, back up, flash, verify, or diagnose ESP32 and ESP32-S3 devices on Windows without confusing COM labels, logs, firmware state, and physical output.'
---

# ESP32 Device Operations

Operate on one identified physical device at a time.

1. Confirm the allowed device and forbidden/frozen devices. Identify the target from current chip/MAC/USB evidence; never treat a remembered COM number as identity.
2. Capture the current port map, firmware/flash facts, and required preservation boundary before mutation.
3. For backup or flashing, read [flash-and-verify.md](references/flash-and-verify.md). Use exact images, offsets, flash size, hashes, and a stop condition.
4. For boot, provisioning, modem, camera, display, microphone, or audio diagnosis, read [runtime-diagnosis.md](references/runtime-diagnosis.md) and trace the physical chain.
5. Report host command success, serial logs, firmware verification, network/service reachability, and physical behavior as separate evidence.

Do not erase NVS, calibration, credentials, partitions, or unrelated boards unless the confirmed task requires it. A log line that says an action ran is not proof that a display, speaker, camera, modem, or network path worked.
