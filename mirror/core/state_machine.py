from enum import Enum, auto


class AgentState(Enum):
    IDLE = auto()
    WATCHING = auto()
    ANALYZING = auto()
    WRITING = auto()
    POSTING = auto()
    SLEEPING = auto()
    PAUSED = auto()
    ERROR = auto()
    INITIALIZING = auto()
    WARMING_UP = auto()


class StateMachine:
    def __init__(self):
        self.state = AgentState.INITIALIZING
        self._callbacks = {}
        self._history = []

    def transition(self, new_state):
        old_state = self.state
        if old_state == new_state:
            return
        self.state = new_state
        self._history.append((old_state, new_state))
        cb = self._callbacks.get(new_state)
        if cb:
            cb(old_state, new_state)

    def on(self, state, callback):
        self._callbacks[state] = callback

    def can_transition(self, new_state):
        allowed = {
            AgentState.IDLE: [AgentState.WATCHING, AgentState.INITIALIZING, AgentState.WARMING_UP],
            AgentState.WATCHING: [AgentState.ANALYZING, AgentState.IDLE, AgentState.SLEEPING, AgentState.PAUSED],
            AgentState.ANALYZING: [AgentState.WRITING, AgentState.WATCHING, AgentState.IDLE],
            AgentState.WRITING: [AgentState.POSTING, AgentState.ANALYZING, AgentState.IDLE],
            AgentState.POSTING: [AgentState.IDLE, AgentState.WATCHING],
            AgentState.SLEEPING: [AgentState.IDLE, AgentState.WARMING_UP],
            AgentState.PAUSED: [AgentState.IDLE, AgentState.SLEEPING],
            AgentState.ERROR: [AgentState.IDLE, AgentState.INITIALIZING],
            AgentState.INITIALIZING: [AgentState.IDLE, AgentState.ERROR, AgentState.WARMING_UP],
            AgentState.WARMING_UP: [AgentState.IDLE, AgentState.WATCHING],
        }
        return new_state in allowed.get(self.state, [])

    def pause(self):
        if self.state not in (AgentState.SLEEPING, AgentState.ERROR):
            self.transition(AgentState.PAUSED)

    def resume(self):
        if self.state == AgentState.PAUSED:
            self.transition(AgentState.IDLE)

    def is_active(self):
        return self.state not in (AgentState.SLEEPING, AgentState.PAUSED, AgentState.ERROR)

    def status_report(self):
        return {
            "current_state": self.state.name,
            "history_count": len(self._history),
            "last_transitions": self._history[-5:] if self._history else [],
        }
