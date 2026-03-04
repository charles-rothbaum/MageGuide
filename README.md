# MageGuide

MageGuide is a Python project for controlling a drone using motion-capture (OptiTrack/NatNet) input.

## Repository layout

- `Drone_Interface.py` – primary entry script for mocap + drone control
- `wandInterface.py` – wand-driven control script
- `Custom_Drone_Commands.py` / `Custom_Drone_Commands_Gazebo.py` – drone command helpers
- `Custom_Mocap_Commands.py` – mocap connection/stream helpers
- `NatNetClient.py`, `MoCapData.py`, `DataDescriptions.py` – NatNet data handling

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install pymavlink
```

Then run one interface script:

```bash
python Drone_Interface.py
# or
python wandInterface.py
```

## Notes

- Make sure your NatNet stream is running before starting the scripts.
- Make sure your drone endpoint/simulator is available on the configured UDP port.
