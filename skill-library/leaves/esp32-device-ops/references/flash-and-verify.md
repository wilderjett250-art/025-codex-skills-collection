# Backup, flash, and verification

1. Enumerate serial devices and probe only the allowed target. Record chip family, MAC, USB adapter/VID-PID where available, flash size, and current port.
2. Before an erase or overwrite, preserve the required ranges or full flash to a verified path. Record file size and hash.
3. Validate the firmware artifact and partition/offset plan against the target chip and flash layout. Do not infer offsets from another board.
4. Prefer a non-booting post-write state when pre-boot verification matters, then run the tool's verify operation or compare read-back hashes.
5. Reboot intentionally, capture boot logs, and verify the requested runtime behavior.

Stop if identity changes, the expected chip/flash size does not match, backup verification fails, a protected device appears, or the image/offset contract is ambiguous.
