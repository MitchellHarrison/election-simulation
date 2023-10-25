import numpy as np
from agent import Agent
from environment import Environment
from dbmanager import DBInterface
from peewee import *

database = SqliteDatabase("simulation.db")

# delete old data every time the model runs
if database.table_exists("sim"):
    database.drop_table("sim")

database.create_tables(["sim"], safe = True)

if __name__ == "__main__":
    env = Environment()

