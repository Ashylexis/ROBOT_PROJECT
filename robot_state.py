import time
import motor_controller


class RobotState:
    STARTUP = "startup"
    IDLE = "idle"
    LOADING_GUNS = "loading_guns"
    FIGHT = "fight"
    FINISHED = "finished"


class RobotStateMachine:
    """High-level robot lifecycle state machine.

    States:
      - STARTUP: system boot and webserver initialization
      - IDLE: waiting for user instructions
      - LOADING_GUNS: prepare the guns for competition
      - FIGHT: execute the selected mission program
      - FINISHED: mission completed, robot is resting
    """

    valid_transitions = {
        RobotState.STARTUP: [RobotState.IDLE],
        RobotState.IDLE: [RobotState.LOADING_GUNS, RobotState.FIGHT, RobotState.FINISHED],
        RobotState.LOADING_GUNS: [RobotState.IDLE, RobotState.FINISHED],
        RobotState.FIGHT: [RobotState.FINISHED],
        RobotState.FINISHED: [RobotState.IDLE],
    }

    def __init__(self):
        self.state = RobotState.STARTUP
        self.selected_mission = None
        self.active_mission = None
        self.state_changed_at = time.ticks_ms()
        print("RobotStateMachine initialisiert: STARTUP")

    def transition_to(self, new_state):
        if self.state == new_state:
            return
        allowed = self.valid_transitions.get(self.state, [])
        if new_state not in allowed:
            print(f"Ungültiger Zustandswechsel: {self.state} -> {new_state}")
            return
        self.state = new_state
        self.state_changed_at = time.ticks_ms()
        print(f"Zustand gewechselt: {self.state}")

    def startup_complete(self):
        self.transition_to(RobotState.IDLE)

    def select_mission(self, mission_id):
        if mission_id not in motor_controller.missions:
            print("Mission nicht gefunden:", mission_id)
            return False
        self.selected_mission = mission_id
        print("Mission ausgewählt:", mission_id)
        return True

    def load_guns(self):
        if self.state != RobotState.IDLE:
            print("Lade Guns abgelehnt, nicht im Idle-Zustand")
            return False
        self.transition_to(RobotState.LOADING_GUNS)
        motor_controller.load_guns()
        time.sleep(1)
        self.transition_to(RobotState.IDLE)
        return True

    def start_fight(self):
        if self.state != RobotState.IDLE:
            print("Start Fight abgelehnt, nicht im Idle-Zustand")
            return False
        if not self.selected_mission:
            print("Keine Mission ausgewählt")
            return False
        self.active_mission = self.selected_mission
        self.transition_to(RobotState.FIGHT)
        if not motor_controller.start_mission(self.active_mission):
            self.transition_to(RobotState.IDLE)
            return False
        return True

    def update(self):
        if self.state == RobotState.FIGHT and not motor_controller.mission_executor.is_running():
            self.transition_to(RobotState.FINISHED)

    def finish(self):
        if self.state == RobotState.FIGHT:
            self.transition_to(RobotState.FINISHED)

    def reset(self):
        self.selected_mission = None
        self.active_mission = None
        if self.state != RobotState.STARTUP:
            self.transition_to(RobotState.IDLE)

    def emergency_stop(self):
        print("Not-Aus: Stoppe alle Motoren")
        for wrapped in (motor_controller.motor_L, motor_controller.motor_R, motor_controller.motor_E):
            try:
                wrapped.stepper.stop(emergency=True)
            except Exception as e:
                print("Fehler beim Stoppen:", e)
        self.reset()

    def status(self):
        return {
            "state": self.state,
            "selected_mission": self.selected_mission,
            "active_mission": self.active_mission,
        }
