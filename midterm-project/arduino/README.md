# Autonomous Line Tracking and RFID Navigation Vehicle

## Overview
This repository contains the firmware for an autonomous line-tracking vehicle. The system integrates infrared line detection, Bluetooth Low Energy (BLE) communication, and RFID reading to navigate a predefined node-based maze. It employs a high-speed Proportional (P) control mechanism for precision tracking and a robust state machine for execution synchronization with a centralized Python server.

## Hardware Dependencies
* **Microcontroller:** Arduino Mega 2560
* **Motor Driver:** TB6612FNG Dual Motor Driver
* **Sensors:** 5-Channel IR Line Tracking Module (TCRT5000)
* **Communication:** HM-10 BLE Module (Serial3)
* **Identification:** MFRC522 RFID Module (SPI interface)
* **Power:** 12.6V Li-ion Battery with Step-Down Buck Converter (5.0V strictly)

## Architecture and File Structure
The project is modularized into distinct operational layers:

1. **`midterm_project.ino` (Main Application)**
   - Houses `setup()` and `loop()`.
   - Manages the core `Search()` state machine.
   - Synchronizes handshake and heartbeat (`READY`) protocols with the remote server.

2. **`track.h` (Locomotion Control)**
   - Implements `MotorWriting` for hardware abstraction.
   - Houses `Tracking_P`, the high-speed Proportional control algorithm featuring line-loss recovery mechanisms to handle sharp deviations.

3. **`node.h` (Intersection Logic)**
   - Defines specific maneuvers (`TurnLeft`, `TurnRight`, `TurnBack`, `Moveforward`) triggered upon intersection detection.
   - Employs bounded motor outputs and delay-based logic for blind intersection clearance.

4. **`bluetooth.h` (Communication)**
   - Handles byte parsing via UART.
   - Maps incoming Python instruction strings (`'f'`, `'b'`, `'r'`, `'l'`, `'h'`, `'s'`) into internal `BT_CMD` enumerations.

5. **`RFID.h` (Identification)**
   - Interfaces with the MFRC522 library to scan and return card UID bytes.

## Protocol and Execution Flow
The vehicle strictly adheres to a request-response protocol to prevent buffer overflows and data desynchronization (Sticky Packets).

1. **Initialization:** Vehicle halts and continuously broadcasts `READY` over BLE.
2. **Ignition:** The Python server transmits `'s'` (START), activating the vehicle's tracking state.
3. **Detection:** Upon reaching a node (intersection), the vehicle halts and broadcasts `'K'`.
4. **Execution:** The vehicle idles dynamically until the server dictates the next node's directional operation.
5. **Completion:** Upon successful maneuver completion, the vehicle transmits a confirmation character (`'L'`, `'R'`, `'B'`, `'F'`, `'S'`) and resumes standard P-control line tracking.