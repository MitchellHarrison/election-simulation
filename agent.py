import scipy.stats as stats

class Agent:
    # these are the parameters required to create an agent and their defaults
    def __init__(self, _id = 1, age = 18, net_worth = 10000, race = "white",
                 politics = "red", education = 1, turnout_mu = 0.5,
                 turnout_s = 1) -> None:
        # this starst with an underscore to differentiate it from the id()
        # function that is built into python
        self.id = _id
        self.age = age
        self.net_worth = net_worth
        self.race = race
        self.politics = politics
        self.education = education

        # establish initial turnout decision distribution
        self.turnout_mu = turnout_mu
        self.turnout_s = turnout_s
        self.turnout_dist = stats.norm(loc = turnout_mu, scale = turnout_s)


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
        Net Worth: ${self.net_worth}
        Political Color: {self.politics}
        Education: {self.education}

        """
        return output
