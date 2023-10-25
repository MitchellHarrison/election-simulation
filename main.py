from agent import Agent
from environment import Environment
from peewee import *

POP_SIZE = 500

database = SqliteDatabase("simulation.db")

# delete old data every time the model runs
if database.table_exists(Agent):
    Agent.drop_table()

database.create_tables([Agent], safe = True)

if __name__ == "__main__":
    env = Environment(pop_size = POP_SIZE)

