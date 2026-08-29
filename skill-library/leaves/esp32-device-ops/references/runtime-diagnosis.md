# Runtime and physical-chain diagnosis

Trace the whole path relevant to the symptom:

- power, USB/serial adapter, port ownership, baud rate, reset/boot mode;
- firmware build/config/partition and preserved NVS;
- peripheral pins, buses, clocks, drivers, initialization, and task state;
- network association, IP, DNS/TLS, API/MQTT/OTA endpoint, and credentials boundary;
- modem AT port, SIM registration, PDP activation, signal, and data path;
- sensor input or actuator output at the physical device.

Use current observations. Distinguish compile success, flash verification, boot logs, service connection, and physical output. When hands-on confirmation is unavailable, name the exact LED/display/audio/camera/network observation still required.
