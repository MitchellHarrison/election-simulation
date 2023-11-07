from agent import Agent
from environment import Environment
from election import Election
from peewee import *

POP_SIZE = 500
MAX_ITERATIONS = 50 

database = SqliteDatabase("simulation.db")

# delete old data every time the model runs
if database.table_exists(Agent):
    Agent.drop_table()

if database.table_exists(Election):
    Election.drop_table()

database.create_tables([Agent, Election], safe = True)

if __name__ == "__main__":
    env = Environment(pop_size = POP_SIZE)
    for _ in range(MAX_ITERATIONS):
        env.iterate()
