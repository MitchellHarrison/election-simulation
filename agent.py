class Agent:
    def __init__(self, id = 1, age = 18, net_worth = 10000, race = "white",
                 politics = "red", education = 1, turnout_likelihood = 0.5):
        self.id = id
        self.age = age
        self.net_worth = net_worth
        self.race = race
        self.politics = politics
        self.education = education
        self.turnout_likelihood = turnout_likelihood

    def __str__(self):
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
