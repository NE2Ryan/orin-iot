# Current Work - Feb 25, 2026

## Tasks Completed
- Updated `orin_gnss.py` to use `/dev/ttyTHS1` for the Jetson Orin Nano UART pins.
- Documented Orin Nano UART mapping in `learnings.md`.

## Status
- `orin_gnss.py` is configured for the Orin Nano hardware UART pins.
- Ready for hardware verification on the Orin.

## Next Steps
- Verify GNSS data reception on the Orin.
- Check permissions if `ttyTHS1` cannot be opened (`sudo usermod -aG dialout $USER`).
