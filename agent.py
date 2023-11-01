import scipy.stats as stats
import numpy as np
from peewee import *

database = SqliteDatabase("simulation.db")

class Agent(Model):
    # this starst with an underscore to differentiate it from the id()
    # function that is built into python
    agent_id = IntegerField(default = 1)

    # incrimented at each model iteration for ease of storage in a single table
    model_iteration = IntegerField(default = 0)

    # agent information
    age = IntegerField(default = 30)
    income = IntegerField(default = 100000)
    race = CharField(default = "White")
    sex = CharField(default = "M")
    politics_score = FloatField(default = 0)
    color = CharField(default = "red")
    education = CharField(default = "Some college")


    # establish initial turnout decision distribution
    turnout_mu = FloatField(default = 0.5)
    turnout_s = FloatField(default = 0.5)
    turnout_dist = stats.norm(loc = turnout_mu, scale = turnout_s)


    # metadata for the database
    class Meta:
        database = database
        table_name = "agents"
        primary_key = False


    # this will update the mean (mu) and variance (s2) of the 
    # turnout distribution
    def update_turnout_dist(self, delta_mu = 0, delta_s = 0) -> None:
        self.turnout_mu += delta_mu
        self.turnout_s += delta_s
        self.turnout_dist = stats.norm(loc = self.turnout_mu, 
                                       scale = self.turnout_s)
        return None

    
    # pull a random value from the turnout likelihood distribution
    def draw_turnout_score(self) -> float:
        draws = self.turnout_dist.rvs(size = 1)
        return draws[0]


    # decide whether or not a voter turns out
    def decide_turnout(self, turnout_threshold = 0.5) -> bool:
        turnout_draw = self.draw_turnout_score()
        if turnout_draw < turnout_threshold:
            return True
        else:
            return False


    # this runs when you print() an agent
    def __str__(self) -> str:
        output = f"""
        Agent {self.id}
        ______________________________________

        Age: {self.age}
        Race: {self.race}
        Net Worth: ${self.income}
        Political Color: {self.color}
        Education: {self.education}

        """
        return output


    # override __init__ for ease of use in modelling
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

