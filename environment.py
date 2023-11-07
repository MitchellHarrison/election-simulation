import scipy.stats as stats
import numpy as np
from agent import Agent
from election import Election

# bin definitions
MAX_AGE = 77
AGE_BINS = [(18,29), (30,49), (50,64), (65,MAX_AGE)]

# "burn-in" removes the first few iterations to approach equilibrium before saving
BURN_IN = 0

# enrollment rate (BLS)
ENROLL_RATE = 0.62

# grad rate (education data initiative)
GRAD_RATE = 0.75

EDU_BINS = ["High school or less", "Some college", "College graduate"]
RACES = ["White", "Black", "Hispanic", "Asian", "Other"]

AGE_MU = 53
AGE_SD = 14

# demographic distributions from Pew
voter_age = [14, 26, 30, 30]
nonvoter_age = [36, 21, 19, 24]

voter_race = [75, 9, 9, 3, 4]
nonvoter_race = [55, 15, 18, 5, 5]

# edu stats are for starting distribution
# new agents will graduate with fixed probability at 21
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


class Environment:
    def __init__(self, p_red = 0.5, pop_size = 10, age_dist = AGE_DIST,
                 education_dist = EDU_DIST, race_dist = RACE_DIST):
        # set environment constants
        self.agents = []
        self.p_red = p_red
        self.p_blue = 1 - p_red
        self.pop_size = pop_size
        self.max_agent_id = 0
        self.current_iteration = 0

        # set environment probability distributions
        self.age_dist = age_dist
        self.education_dist = education_dist
        self.race_dist = race_dist

        # create agents in environment
        self.agents = self.setup_agents()

        # list of peewee objects to store data from agents
        self.agent_stores = []

        # keep track of current party in power
        self.prev_winner = "red"


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
        agent.politics_score += AGE_POL * age_from_start / 1.3

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


    # create agents in the simulation from given distributions
    def setup_agents(self):
        agent_id = 1
        agents = []
        for _ in range(self.pop_size):
            agent = Agent()

            # create an agent from relevant distributions passed to the env
            agent.agent_id = agent_id
            agent.election_year = 0
            age = -1

            # keep ages in the appropriate range
            while age < 18 or age > 77:
                age = int(stats.norm.rvs(AGE_MU, AGE_SD, size = 1))

            agent.age = age
            agent.sex = np.random.choice(["M", "F"], p = (0.5, 0.5))

            # women turnout slightly more than men
            if agent.sex == "F":
                agent.turnout_mu += 0.1

            agent.politics_score = 0
            agent.race = np.random.choice(RACES, p = self.race_dist)

            # -1 to 1 score for more liberal/conservative
            self.adjust_starting_politics(agent)

            agent.education = np.random.choice(EDU_BINS, 
                                               p = self.education_dist)
            agent.model_iteration = 0

            # append this new agent to the environment's agents list
            agents.append(agent)
            agent_id += 1
            self.max_agent_id += 1

        return agents


    # calculate the outcome of an election from current agent status
    # return "red" or "blue" that is the winning party
    def run_election(self) -> str:
        blue_count = 0
        red_count = 0

        for agent in self.agents:
            agent.election_year = 1
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
                agent.voted = 1
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

        if self.current_iteration > BURN_IN:
            election = Election(
                    model_iteration = self.current_iteration, 
                    red_count = red_count, 
                    blue_count = blue_count, 
                    winner = winner
                )
            print(f"Winner: {winner.title()}")
            election.save()

        return winner


    # re-calculate an agent's education outcome
    def get_education(self) -> str:
        edu = "High school or less"
        p_college = np.random.random()
        if p_college <= ENROLL_RATE:
            p_graduated = np.random.random()
            if p_graduated <= GRAD_RATE:
                edu = "College graduate"
            else:
                edu = "Some college"
        return edu


    # run a single iteration of the simulation, changing agents as required
    def iterate(self) -> None:
        self.current_iteration += 1

        # check for election year
        election_year = 1 if self.current_iteration % 4 == 0 else 0
        if election_year:
            self.prev_winner = self.run_election()

        for i, agent in enumerate(self.agents):
            agent.model_iteration = self.current_iteration

            agent.election_year = election_year
            if not election_year:
                agent.voted = 0

            agent.age += 1

            # check to see if agent graduated college at 21
            if agent.age == 21:
                agent.education = self.get_education()

            # check for agent death, replace with 18 year old of same race
            # mean and standard deviation from NIH
            death_threshold = stats.norm.rvs(loc = 77, scale = 15, size = 1)
            if agent.age > MAX_AGE or agent.age >= death_threshold:
                new_agent = Agent()
                new_agent.race = agent.race
                age = -1

                # keep ages in the appropriate range
                while age < 18 or age > 77:
                    age = int(stats.norm.rvs(AGE_MU, AGE_SD, size = 1))

                new_agent.age = age
                new_agent.sex = np.random.choice(["M", "F"], p = (0.5, 0.5))
                new_agent.turnout_mu = 0.5
                self.adjust_starting_politics(new_agent)
                self.max_agent_id += 1
                new_agent.model_iteration = self.current_iteration
                new_agent.agent_id = self.max_agent_id

                # adjust starting politics based on demographics
                self.adjust_starting_politics(new_agent)
                
                self.agents[i] = new_agent
                agent = new_agent

            # if agent doesn't die
            else:
                # decide if a person graduated college
                if agent.age > 22:
                    agent.education = self.get_education()

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

                # move agents away from sitting party (historc trend)
                if self.prev_winner == "red":
                    agent.politics_score -= 0.02
                else:
                    agent.politics_score += 0.02
                
                agent.update_turnout_dist()
                agent.update_color()

            # save updated agent data
            if self.current_iteration < BURN_IN:
                return
            agent.save()


    # print the parameters for each agent (useful for debugging)
    def display_agents(self):
        for a in self.agents:
            print(a)
