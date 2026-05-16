import numpy as np

from mesa import Model
from agents import Student
from agents import University
from mesa.experimental.continuous_space import ContinuousSpace

class UniversityRevenue(Model):
    ## Initialize model, including all relevant parameters. Inherit seed propety from parent class
    def __init__(
        self,
        student_count=100,
        university_count=5,
        donate = 1,
        capacity_prop = .5,
        information = "No information",
        seed=None,
    ):
        if seed is not None:
            seed = int(seed)
        super().__init__(rng=seed)
        # Set up the continuous space
        self.space = ContinuousSpace(
            [[0,1], [0,1]],
            torus=False,
            random=self.random,
            n_agents=student_count+university_count
        )
        student_positions = [(0, i) for i in self.rng.uniform(0,1,size=student_count)]
        university_positions = [(.5,i) for i in np.linspace(.1, .9, university_count)]
        wealths = self.rng.uniform(0,1,size=student_count)
        merits = self.rng.uniform(0,1,size=student_count)
        tuitions = self.rng.uniform(0,1,size=university_count)
        prestiges = self.rng.uniform(0,1,size=university_count)

        self.donate = donate
        self.capacity = capacity_prop * student_count
        self.information = information
        ## Create agents and place them on the map
        Student.create_agents(
            self,
            student_count,
            self.space,
            position = student_positions,
            wealth = wealths,
            merit = merits
        )
        University.create_agents(
            self,
            university_count,
            self.space,
            position = university_positions,
            tuition = tuitions,
            prestige = prestiges
        )
    ## Define model step
    def step(self):
        self.agents.do("reset")
        self.agents_by_type[University].do("offer")
        self.agents_by_type[Student].do("accept")
        self.agents_by_type[University].do("waitlist")
        self.agents_by_type[Student].do("accept")
        self.agents_by_type[University].do("update_prestige")
