import numpy as np
from agent import Agent

# bin definitions
AGE_BINS = [(18,29), (30,49), (50,64), (65,77)]

# median household income from Capital One
INCOME_BINS = [45604, 59150, 59228 , 57252]

EDU_BINS = ["High School or Less", "Some college", "College graduate"]
RACES = ["White", "Black", "Hispanic", "Asian", "Other"]

# demographic distributions from Pew
voter_age = [10, 26, 30, 34]
nonvoter_age = [27, 37, 22, 14]

voter_race = [75, 9, 9, 3, 4]
nonvoter_race = [55, 15, 18, 5, 5]

voter_edu = [25, 31, 24 + 19]
nonvoter_edu = [43, 31, 16 + 10]

# calculate means of voters and non-voters to generalize the population
def average_lists(list1, list2) -> list:
    avg_lists_as_pct = [((x + y) / 2) / 100 for x, y in zip(list1, list2)] 

    # correct rounding error by rounding last element up to sum to 1 total
    if sum(avg_lists_as_pct) != 1:
        all_but_last = avg_lists_as_pct[:-1]
        concrete_sum = sum(all_but_last)
        rounded_last = 1 - concrete_sum
        avg_lists_as_pct[len(avg_lists_as_pct)-1] = rounded_last

    return avg_lists_as_pct

AGE_DIST = average_lists(voter_age, nonvoter_age)
RACE_DIST = average_lists(voter_race, nonvoter_race)
EDU_DIST = average_lists(voter_edu, nonvoter_edu)
INCOME_DIST = [.25, .25, .25, .25]


class Environment:
    def __init__(self, p_red = 0.5, pop_size = 10, age_dist = AGE_DIST,
                 income_dist = INCOME_DIST, education_dist = EDU_DIST, 
                 race_dist = RACE_DIST, past_winners = []):
        # set environment constants
        self.agents = []
        self.p_red = p_red
        self.p_blue = 1 - p_red
        self.pop_size = pop_size
        self.prev_winner = past_winners

        # set environment probability distributions
        self.age_dist = age_dist
        self.income_dist = income_dist
        self.education_dist = education_dist
        self.race_dist = race_dist

        # create agents in environment
        self.agents = self.setup_agents()

        # list of peewee objects to store data from agents
        self.agent_stores = []


    # create agents in the simulation from given distributions
    def setup_agents(self):
        agent_id = 1
        agents = []
        for _ in range(self.pop_size):
            agent = Agent()

            # create an agent from relevant distributions passed to the env
            agent._id = agent_id
            age_bin = np.random.choice([0, 1, 2, 3], p = self.age_dist)
            age_range = AGE_BINS[age_bin]
            agent.age = np.random.randint(age_range[0], age_range[1] + 1, 1)
            agent.color = np.random.choice(["red", "blue"], 
                                           p = [self.p_red, self.p_blue])
            agent.net_worth = np.random.choice(INCOME_BINS, 
                                               p = self.income_dist)
            agent.education = np.random.choice(EDU_BINS, 
                                               p = self.education_dist)
            agent.race = np.random.choice(RACES, p = self.race_dist)
            agent.model_iteration = 0

            # append this new agent to the environment's agents list
            agents.append(agent)
            agent_id += 1

            # store starting contitions
            agent.save()
        return agents


    # calculate the outcome of an election from current agent status
    # return "red" or "blue" that is the winning party
    def run_election(self) -> str:
        blue_count = 0
        red_count = 0

        for agent in self.agents:
            # TODO: decide turnout
            continue

        return


    # run a single iteration of the simulation, changing agents as required
    def iterate(self) -> None:
        for agent in self.agents:
            agent.model_iteration += 1
            agent.age += 1
            agent.turnout_mu += 0.006 # up per year of age
            # TODO: update mu up and down with varying distributions


    # setup list of agent models for storage
    def setup_agent_stores(self) -> list:
        for a in self.agents:
            continue


    # print the parameters for each agent (useful for debugging)
    def display_agents(self):
        for a in self.agents:
            print(a)
