import numpy as np
from agent import Agent

# bin definitions
AGE_BINS = ["18-22", "23-28", "29-35", "36-45", "46-55", "56-65", "65+"]
WORTH_BINS = ["0-10,000", "10,001-100,000", "100,001-500,000",
              "500,001-1,000,000", "1,000,001+"]
EDU_BINS = ["No High School", "High School", "Undergraduate", "Graduate"]
RACES = ["White", "Black", "Hispanic", "Asian", "Other"]

class Environment:
    def __init__(self, p_red = 0.5, pop_size = 10, age_dist = [],
                 income_dist = [], education_dist = [], race_dist = []):
        # set environment constants
        self.agents = []
        self.p_red = p_red
        self.p_blue = 1 - p_red
        self.pop_size = pop_size

        # set environment probability distributions
        self.age_dist = age_dist
        self.income_dist = income_dist
        self.education_dist = education_dist
        self.race_dist = race_dist

        # create agents in environment
        self.agents = self.setup_agents()


    # create agents in the simulation from given distributions
    def setup_agents(self):
        agent_id = 1
        agents = []
        for _ in range(self.pop_size):
            agent = Agent()

            # create an agent from relevant distributions passed to the env
            agent.id = agent_id
            agent.age = np.random.choice(AGE_BINS, p = self.age_dist)
            agent.politics = np.random.choice(["red", "blue"], 
                                              p = [self.p_red, self.p_blue])
            agent.net_worth = np.random.choice(WORTH_BINS, p = self.income_dist)
            agent.education = np.random.choice(EDU_BINS, p = self.education_dist)
            agent.race = np.random.choice(RACES, p = self.race_dist)

            # append this new agent to the environment's agents list
            agents.append(agent)
            agent_id += 1
        return agents

    # print the parameters for each agent (useful for debugging)
    def display_agents(self):
        for a in self.agents:
            print(a)
