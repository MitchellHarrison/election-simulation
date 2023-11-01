from agent import Agent
from peewee import *

database = SqliteDatabase("simulation.db")

class Election(Model):
    model_iteration = IntegerField(default = 4)
    red_count = IntegerField(default = 0)
    blue_count = IntegerField(default = 0)
    winner = CharField(default = "red")

    class Meta:
        database = database
        table_name = "elections"
        primary_key = False
