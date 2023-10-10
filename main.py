import numpy as np
from agent import Agent
from environment import Environment

P_RED = 0.5
POP_SIZE = 20
AGE_DIST = [.2, .2, .2, .2, .1, .05, .05]
EDU_DIST = [.25, .25, .25, .25]
RACE_DIST = [.2, .2, .2, .2, .2]
WORTH_DIST = [.2, .2, .2, .2, .2]


if __name__ == "__main__":
    env = Environment(P_RED, POP_SIZE, AGE_DIST, WORTH_DIST, EDU_DIST, RACE_DIST)
    env.display_agents()
