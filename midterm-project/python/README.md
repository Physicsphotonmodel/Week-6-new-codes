# PC Control & Routing System for Autonomous Vehicle

## Overview
This repository contains the Python-based mission control application. It operates asynchronously to generate dynamic graph-based routing logic, manage real-time Bluetooth Low Energy (BLE) transmissions with the hardware, and securely dispatch discovery events to a remote server. 

## File Structure
Based on the defined project layout, the root `python` directory is structured as follows:

```
python/
├── data/                  # Directory containing topological node maps (CSV)
├── hm10_bleak/            # BLE driver package managing async serial-over-bluetooth 
├── main.py                # Primary asynchronous execution and state machine hub
├── maze.py                # Graph management and time-bound greedy pathfinding logic
├── node.py                # Directional enums and Node data structure
├── requirements.txt       # Python environment dependencies
└── score.py               # Socket.IO client interface for remote scorekeeping
```

## Module Descriptions

* **`main.py`**
  Serves as the central control loop. Evaluates command line arguments, requests optimal path generation, manages the handshake sequence via the BLE interface, and monitors the incoming telemetry stream to dispatch appropriate navigation directives (`f`, `b`, `l`, `r`).
* **`maze.py`**
  Parses geographical representation matrices (`.csv`). Includes fundamental Breadth-First Search (`BFS`) alongside a robust "Pacman" strategy algorithm that estimates physical kinematic time thresholds to maximize score acquisition within strict operational limits.
* **`node.py`**
  Constructs discrete node topologies. Abstracts physical directional mappings into standardized enumerations (`NORTH`, `SOUTH`, `WEST`, `EAST`) to support reliable adjacent traversal mappings.
* **`score.py`**
  Implements the API interactions bridging the local system and the scoring server. Submits acquired `UID` strings for validation and logs active payload scores. Contains `ScoreboardFake` for development isolated from live environments.

## Usage
Execute the entry script with the targeted operational mode. Mode `0` triggers standard automated competition routing.

```bash
python main.py 0  --team-name "WED7" --maze-file "data/small_maze.csv"
```

Ensure all dependencies from `requirements.txt` are successfully installed within your virtual environment prior to execution.