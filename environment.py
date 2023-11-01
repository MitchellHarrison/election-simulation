import scipy.stats as stats
import numpy as np
from agent import Agent
from election import Election

# bin definitions
MAX_AGE = 77
AGE_BINS = [(18,29), (30,49), (50,64), (65,MAX_AGE)]

# median income from Capital One
INCOME_BINS = [45604, 59150, 59228 , 57252]

EDU_BINS = ["High School or Less", "Some college", "College graduate"]
RACES = ["White", "Black", "Hispanic", "Asian", "Other"]

AGE_MU = 52
AGE_SD = 14

# demographic distributions from Pew
voter_age = [10, 26, 30, 34]
nonvoter_age = [27, 37, 22, 14]

voter_race = [75, 9, 9, 3, 4]
nonvoter_race = [55, 15, 18, 5, 5]

voter_edu = [25, 31, 24 + 19]
nonvoter_edu = [43, 31, 16 + 10]

# intervals to increase per iteration
AGE_POL = 0.01
BLACK_POL = 0.76
HISPANIC_POL = 0.35
ASIAN_POL = 0.38
FEMALE_POL = 0.19

# threshold that decides whether or not someone turns out
TURNOUT_THRESH = 0.5

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
        self.max_agent_id = 0
        self.current_iteration = 0

        # set environment probability distributions
        self.age_dist = age_dist
        self.income_dist = income_dist
        self.education_dist = education_dist
        self.race_dist = race_dist

        # create agents in environment
        self.agents = self.setup_agents()

        # list of peewee objects to store data from agents
        self.agent_stores = []


    """
    Subtraction numbers are calculated by the percent of 2017
    voters that were Republicans for each race/sex from the percent
    that voted Democrat. That difference is the amount subtracted
    from the starting 0 below.
    """
    # adjust starting politics based on current demographics
    def adjust_starting_politics(self, agent) -> Agent:
        # corrent for age
        age_from_start = agent.age - 18
        agent.politics_score += AGE_POL * age_from_start

        # adjust starting politics by race (Pew)
        if agent.race == "Black":
            agent.politics_score -= BLACK_POL
        elif agent.race == "Hispanic":
            agent.politics_score -= HISPANIC_POL
        elif agent.race == "Asian":
            agent.politics_score -= ASIAN_POL

        # correct for sex (Pew)
        if agent.sex == "F":
            agent.politics_score -= FEMALE_POL

        # assign color, breaking ties arbitrarily
        if agent.politics_score == 0:
            agent.color = np.random.choice(["red", "blue"], p = (0.5, 0.5))
        elif agent.politics_score < 0:
            agent.color = "blue"
        else:
            agent.color = "red"

        return agent


    # create agents in the simulation from given distributions
    def setup_agents(self):
        agent_id = 1
        agents = []
        for _ in range(self.pop_size):
            agent = Agent()

            # create an agent from relevant distributions passed to the env
            agent.agent_id = agent_id
            age = -1

            # keep ages in the appropriate range
            while age < 18 or age > 77:
                age = stats.norm.rvs(AGE_MU, AGE_SD, size = 1)

            agent.age = age
            agent.sex = np.random.choice(["M", "F"], p = (0.5, 0.5))
            agent.race = np.random.choice(RACES, p = self.race_dist)

            # -1 to 1 score for more liberal/conservative
            agent = self.adjust_starting_politics(agent)

            agent.net_worth = np.random.choice(INCOME_BINS, 
                                               p = self.income_dist)
            agent.education = np.random.choice(EDU_BINS, 
                                               p = self.education_dist)
            agent.model_iteration = 0

            # append this new agent to the environment's agents list
            agents.append(agent)
            agent_id += 1
            self.max_agent_id += 1

            agent.save()
                    
        return agents


    # calculate the outcome of an election from current agent status
    # return "red" or "blue" that is the winning party
    def run_election(self) -> str:
        blue_count = 0
        red_count = 0

        for agent in self.agents:
            mu = agent.turnout_mu
            is_centrist = -0.1 <= mu <= 0.1
            turnout_draw = agent.draw_turnout_score()

            # if voter decides to vote
            if is_centrist:
                vote = stats.norm.rvs(loc = mu, scale = 0.1, size = 1)
                if vote >= 0:
                    color = "red"
                else:
                    color = "blue"
            else:
                color = agent.color

            if turnout_draw >= TURNOUT_THRESH:
                if color == "red":
                    red_count += 1
                else:
                    blue_count += 1

        # break unlikely ties arbitrarily
        winner = ""
        if red_count == blue_count:
            winner = np.random.choice(["red", "blue"], p = (0.5, 0.5))
        elif red_count > blue_count:
            winner = "red"
        else:
            winner = "blue"

        election = Election(
                model_iteration = self.current_iteration, 
                red_count = red_count, 
                blue_count = blue_count, 
                winner = winner
            )
        election.save()

        return winner


    # run a single iteration of the simulation, changing agents as required
    def iterate(self) -> None:
        self.current_iteration += 1
        if self.current_iteration % 4 == 0:
            winner = self.run_election()
            print(winner)

        for (i, agent) in enumerate(self.agents):
            agent.model_iteration = self.current_iteration

            agent.age += 1

            # check for agent death, replace with 18 year old of same race
            if agent.age > MAX_AGE:
                new_agent = Agent()
                new_agent.race = agent.race
                new_agent.age = 18
                new_agent.sex = np.random.choice(["M", "F"], p = (0.5, 0.5))
                new_agent.turnout_mu = 0.5
                new_agent.politics_score = 0
                self.max_agent_id += 1
                new_agent.model_iteration = self.current_iteration
                new_agent.agent_id = self.max_agent_id

                # adjust starting politics based on demographics
                new_agent = self.adjust_starting_politics(new_agent)
                
                self.agents[i] = new_agent
                agent = new_agent

            # if agent doesn't die
            else:
                # decide if a person graduated college
                if agent.age == 22:
                    agent.education = np.random.choice(EDU_BINS, p = EDU_DIST)

                # move centrists more conservative per year (Pew)
                politics_dist = stats.norm(loc = 0, scale = 1)
                lower = politics_dist.ppf(.3)
                upper = politics_dist.ppf(.7)
                is_centrist = lower <= agent.politics_score <= upper

                # the following applies only to centrists (Pew)
                if is_centrist:
                    # move left if educated over time (Pew)
                    if agent.education == "Some college": 
                        agent.politics_score -= 0.015
                    elif agent.education == "College graduate":
                        agent.politics_score -= 0.025

                    # move right with age (Pew)
                    agent.politics_score += 0.01 # for age
                
            # save updated agent data
            agent.save()


    # print the parameters for each agent (useful for debugging)
    def display_agents(self):
        for a in self.agents:
            print(a)
