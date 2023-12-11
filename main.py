import numpy as np
from agent import Agent
from environment import Environment
from election import Election
from peewee import *

SEED = 427
np.random.seed(SEED)

POP_SIZE = 100
MAX_ITERATIONS = 100 

database = SqliteDatabase("simulation.db")

# delete old data every time the model runs
if database.table_exists(Agent):
    Agent.drop_table()

if database.table_exists(Election):
    Election.drop_table()

database.create_tables([Agent, Election], safe = True)

EDU_DIST = [0.3, 0.3, 0.4]

if __name__ == "__main__":
    env = Environment(pop_size = POP_SIZE, education_dist = EDU_DIST)
    for _ in range(MAX_ITERATIONS):
        env.iterate()
