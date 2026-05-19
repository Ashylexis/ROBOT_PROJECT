# ROBOT_PROJECT Software Architecture

## Overview

The robot software is divided into three main responsibilities:

- `main.py`: startup, network/web server, HTTP handling, and the robot lifecycle entry point.
- `robot_state.py`: high-level robot state machine and lifecycle management.
- `motor_controller.py`: actuator control, servo logic, stepper movement, and mission execution.
- `missions.py`: simple mission table definitions for fight programs.

## State Machine

The robot lifecycle uses a state machine with the following states:

1. **Startup**
   - Begin after boot.
   - Start the Wi-Fi access point and web server.
   - Initialize LEDs and hardware.
   - Transition to `Idle` when ready.

2. **Idle**
   - Robot waits for user commands.
   - Commands can select a mission, load guns, or start a fight.

3. **Loading Guns**
   - Prepares the guns for competition.
   - Moves servos to the loaded position.
   - Returns to `Idle` when complete.

4. **Fight**
   - Executes the chosen mission program.
   - Runs the sequence of drive, gun, and fire actions.
   - Transitions to `Finished` after mission execution.

5. **Finished**
   - The robot rests after a fight.
   - Allows reset back to `Idle` or emergency stop.

## Transitions

- `Startup -> Idle`
- `Idle -> Loading Guns`
- `Idle -> Fight`
- `Loading Guns -> Idle`
- `Fight -> Finished`
- `Finished -> Idle`

## Modules

### `main.py`

- Starts the robot and hardware.
- Creates the web server.
- Uses `RobotStateMachine` to reflect current lifecycle.
- Receives HTTP commands and dispatches them into the state machine.

### `robot_state.py`

- Defines the state constants and transition rules.
- Controls mission selection, gun loading, fight execution, reset, and emergency stop.
- Keeps the robot in valid lifecycle states.

### `motor_controller.py`

- Controls servos and stepper motors.
- Defines mission sequences (`p1`, `p2`, `p3`).
- Exposes mission execution and gun-loading helpers.

## Behavior

- The robot only starts a mission when in `Idle`.
- Gun loading is only allowed from `Idle`.
- After a mission, the robot moves to `Finished` before it can return to `Idle`.
- Emergency stop interrupts ongoing motion and resets to `Idle`.

## Notes

- The state machine is intentionally simple and deterministic.
- Commands should be implemented in the web UI to match the state transitions.
- This architecture keeps high-level lifecycle concerns separate from low-level motor control.
