import scipy.stats as stats
import numpy as np
from peewee import *

database = SqliteDatabase("simulation.db")

# the notch size denotes the positive or negative change to 
NOTCH_SIZE = 0.01

class Agent(Model):
    # this starst with an underscore to differentiate it from the id()
    # function that is built into python
    agent_id = IntegerField(default = 1)

    # incrimented at each model iteration for ease of storage in a single table
    model_iteration = IntegerField(default = 0)

    # boolean variable that is 1 when there is an election
    election_year = IntegerField(default = 0)

    # if election_year == 1 then voted will be 1 if they turned out to vote
    voted = IntegerField(default = 0)

    # whether or not a voter is an extremist
    is_extreme = IntegerField(default = 0)

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
    turnout_s = FloatField(default = 0.1)
    turnout_dist = stats.norm(loc = turnout_mu, scale = turnout_s)


    # metadata for the database
    class Meta:
        database = database
        table_name = "agents"
        primary_key = False


    # calculate the updated mean of turnout distribution
    def calculate_mu(self):
        new_mu = 0
        # adjust turnout based on age (Pew)
        if self.age > 64:
            new_mu += 1.5 * NOTCH_SIZE
        elif self.age > 50:
            new_mu += NOTCH_SIZE
        elif self.age > 30:
            new_mu -= NOTCH_SIZE
        else:
            new_mu -= 2 * NOTCH_SIZE

        # adjust turnout based on education (Pew)
        if self.education == "High school or less":
            new_mu -= 2 * NOTCH_SIZE
        elif self.education == "College graduate":
            new_mu += 2 * NOTCH_SIZE

        # extremists vote more
        if self.is_extreme:
            new_mu += NOTCH_SIZE

        # if a person is highly partisain, they vote more often
        if np.abs(self.politics_score) > 0.3:
            new_mu += NOTCH_SIZE

        return new_mu

    # this will update the mean (mu) and variance (s2) of the 
    # turnout distribution
    def update_turnout_dist(self, delta_s = 0) -> None:
        self.turnout_mu += self.calculate_mu()
        self.turnout_s += delta_s
        self.turnout_dist = stats.norm(loc = self.turnout_mu, 
                                       scale = self.turnout_s)
        return None

    
    # check for party switch
    def update_color(self):
        if self.politics_score < 0:
            self.color = "blue"
        else:
            self.color = "red"


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
        Agent
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

