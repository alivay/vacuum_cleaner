import numpy as np
from dataclasses import dataclass
import enum

NUM_AGENTS=1
ROOM_WIDTH=10
ROOM_HEIGHT=10
MAX_ITERATIONS=50

class TileStatus(enum.Enum):
    CLEAN = 0
    DIRTY = 1
    BLOCKED = 2

class Power(enum.Enum):
    OFF = 0
    ON = 1
    UNKNOWN = 2

class Direction(enum.Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

class Action(enum.Enum):
    NOP = 0
    GO_FORWARD = 1
    TURN_RIGHT = 2
    TURN_LEFT = 3
    SUCK_UP_DIRT = 4
    TURN_OFF = 5

class Agent:
    static_index = 0
    def __init__(self):
        self.index = Agent.static_index
        Agent.static_index+=1
        self.first_time=True
    def __repr__(self):
        return "Agent(" + str(self.index) + ")"

@dataclass
class Room:
    def __init__(self):
        self.room = [[TileStatus.CLEAN for x in range(ROOM_WIDTH)] for y in range(ROOM_HEIGHT)]
        self.room[1][2] = TileStatus.DIRTY
        self.room[4][3] = TileStatus.DIRTY
        self.room[5][4] = TileStatus.BLOCKED
        self.room[5][5] = TileStatus.BLOCKED
        self.room[5][6] = TileStatus.BLOCKED
        self.room[5][7] = TileStatus.BLOCKED
        self.room[5][8] = TileStatus.BLOCKED
        for i in range(ROOM_WIDTH):
            self.room[i][0] = self.room[i][ROOM_HEIGHT-1] = TileStatus.BLOCKED
        for i in range(ROOM_HEIGHT):
            self.room[0][i] = self.room[ROOM_HEIGHT-1][i] = TileStatus.BLOCKED

    def __repr__(self):
        str = ""
        for row in range(ROOM_HEIGHT-1, -1, -1):
            for col in range(ROOM_WIDTH):
                if self.room[row][col] == TileStatus.CLEAN:
                    str += ". "
                elif self.room[row][col] == TileStatus.BLOCKED:
                    str += "B "
                elif self.room[row][col] == TileStatus.DIRTY:
                    str += "D "
            str += '\n'
        return str

    def is_dirty(self, x, y):
        return self.room[x][y] == TileStatus.DIRTY

    def is_blocked(self, x, y):
        return self.room[x][y] == TileStatus.BLOCKED
    
    def clean(self, x, y):
        self.room[x][y] = TileStatus.CLEAN

    def get_tile(self,x,y):
        return self.room[x][y]

@dataclass
class AgentState:
    def __init__(self, x, y, facing):
        self.state = Power.UNKNOWN
        self.bumped = False
        self.last_move_score = 0
        self.x = x
        self.y = y
        self.facing = facing
        self.home_x = x
        self.home_y = y

    def __repr__(self):
        return "AgentState(state=" + str(self.state) + ", x=" + str(self.x) + ", y=" + str(self.y) + ", facing=" + str(self.facing) + ")\n"

@dataclass
class State:
    def __init__(self):
        self.room = Room()
        self.agents_state = []
        for i in range(NUM_AGENTS):
            agent_state = AgentState(1, 1, Direction.NORTH)
            self.agents_state.append(agent_state)
        self.iterations=0

    def __repr__(self):
        str = ""
        for row in range(ROOM_HEIGHT - 1, -1, -1):
            for col in range(ROOM_WIDTH):
                tile = self.room.get_tile(col, row)
                if self.agents_state[0].x == col and self.agents_state[0].y == row:
                    str += "0 "
                elif tile == TileStatus.CLEAN:
                    str += ". "
                elif tile == TileStatus.BLOCKED:
                    str += "B "
                elif tile == TileStatus.DIRTY:
                    str += "D "
            str += '\n'
        return str

@dataclass
class Percept:
    def __init__(self):
        self.touch_sensor = 0
        self.dirty_sensor = 0
        self.home_sensor = 0

def termination(state):
    if state.iterations == MAX_ITERATIONS:
        return True
    for agent_state in state.agents_state:
        if agent_state.state != Power.OFF:
            return False
    return True

def get_percept(agent, state):
    index = agent.index
    agent_state = state.agents_state[index]
    touch_sensor = 1 if agent_state.bumped else 0
    dirty_sensor = 1 if state.room.is_dirty(agent_state.x,agent_state.y) else 0
    home_sensor = 1 if agent_state.x == agent_state.home_x and agent_state.y == agent_state.home_y else 0
    return touch_sensor, dirty_sensor, home_sensor

def program(agent,percept):
    touch_sensor = percept[0]
    dirty_sensor = percept[1]
    home_sensor = percept[2]
    print("program: touch_sensor = {}, dirty_sensor = {}, home_sensor = {}".format(touch_sensor, dirty_sensor, home_sensor))
    if home_sensor:
        if not agent.first_time:
            return Action.TURN_OFF
    agent.first_time = False
    if touch_sensor:
        return Action.TURN_RIGHT
    elif dirty_sensor:
        return Action.SUCK_UP_DIRT
    else:
        return Action.GO_FORWARD

def update_fn(actions, agents, state):
    for i in range(NUM_AGENTS):
        state.agents_state[i].last_move_score=-1
        state.agents_state[i].bumped=0
        agents[i].first_time=False;
        if actions[i] == Action.GO_FORWARD:
            target_x = target_y = 0
            if state.agents_state[i].facing == Direction.NORTH:
                target_x = state.agents_state[i].x
                target_y = state.agents_state[i].y+1
            elif state.agents_state[i].facing == Direction.EAST:
                target_x = state.agents_state[i].x+1
                target_y = state.agents_state[i].y
            elif state.agents_state[i].facing == Direction.SOUTH:
                target_x = state.agents_state[i].x
                target_y = state.agents_state[i].y-1
            elif state.agents_state[i].facing == Direction.WEST:
                target_x = state.agents_state[i].x-1
                target_y = state.agents_state[i].y
            else:
                exit(1)
            if state.room.is_blocked(target_x, target_y):
                state.agents_state[i].bumped = 1
            else:
                state.agents_state[i].x = target_x
                state.agents_state[i].y = target_y
        elif actions[i] == Action.TURN_RIGHT:
            if state.agents_state[i].facing == Direction.NORTH:
                state.agents_state[i].facing = Direction.EAST
            elif state.agents_state[i].facing == Direction.EAST:
                state.agents_state[i].facing = Direction.SOUTH
            elif state.agents_state[i].facing == Direction.SOUTH:
                state.agents_state[i].facing = Direction.WEST
            elif state.agents_state[i].facing == Direction.WEST:
                state.agents_state[i].facing = Direction.NORTH
            else:
                exit(1)
        elif actions[i] == Action.TURN_LEFT:
            if state.agents_state[i].facing == Direction.NORTH:
                state.agents_state[i].facing = Direction.WEST
            elif state.agents_state[i].facing == Direction.EAST:
                state.agents_state[i].facing = Direction.NORTH
            elif state.agents_state[i].facing == Direction.SOUTH:
                state.agents_state[i].facing = Direction.EAST
            elif state.agents_state[i].facing == Direction.WEST:
                state.agents_state[i].facing = Direction.SOUTH
            else:
                exit(1)
        elif actions[i] == Action.SUCK_UP_DIRT:
            state.room.clean(state.agents_state[i].x, state.agents_state[i].y)
            state.agents_state[i].last_move_score += 100
        elif actions[i] == Action.TURN_OFF:
            state.agents_state[i].state = Power.OFF
            if state.agents_state[i].x != state.agents_state[i].home_x or state.agents_state[i].y != state.agents_state[i].home_y:
                state.agents_state[i].last_move_score -= 1000
    state.iterations += 1
    return state

def performance_fn(scores, agents, state):
    for agent in agents:
        index = agent.index
        scores[index] += state.agents_state[index].last_move_score
    return scores

def run_eval_environment(state, agents, termination):
    scores = [0]*NUM_AGENTS
    count = 0;
    while not termination(state):
        print(state)
        for agent in agents:
            touch_sensor, dirty_sensor, home_sensor = get_percept(agent, state)
            percepts[agent.index] = [touch_sensor, dirty_sensor, home_sensor]
        for agent in agents:
            actions[agent.index] = program(agent, percepts[agent.index])
            print("actions[{}] = {}".format(agent.index, actions[agent.index]))
        state = update_fn(actions, agents, state)
        scores = performance_fn(scores, agents, state)
    return scores

state = State()

agents = []
for i in range(NUM_AGENTS):
    agent = Agent()
    agents.append(agent)

percepts =[]
for i in range(NUM_AGENTS):
    percept = Percept()
    percepts.append(percept)

actions = [Action.NOP] * NUM_AGENTS

scores = run_eval_environment(state, agents, termination)
print("scores = {}".format(scores))