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
        # Set up the continuous space. This is used purely for visualization
        # and not for any decisions
        self.space = ContinuousSpace(
            [[0,1], [0,1]],
            torus=False,
            random=self.random,
            n_agents=student_count+university_count
        )
        student_positions = [(0, i) for i in self.rng.uniform(0,1,size=student_count)]
        university_positions = [(.5,i) for i in np.linspace(.1, .9, university_count)]
        # Agent attributes are all set with uniform random distributions betwen 0 and 1
        wealths = self.rng.uniform(0,1,size=student_count)
        merits = self.rng.uniform(0,1,size=student_count)
        # Tuition is caluclated here, even though the current implementation
        # uses the same value for prestige and tuition
        tuitions = self.rng.uniform(0,1,size=university_count)
        prestiges = self.rng.uniform(0,1,size=university_count)

        # The coefficient for alumni donation expectation
        self.donate = donate
        # The relative capacity of each university
        self.capacity = capacity_prop * student_count
        # The degree of financial information for students to hold
        self.information = information
        ## All agents are initialized with random attribute values
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
        # The reset is placed here instead of last to maintain vizualization
        self.agents.do("reset")
        # Universities extend their first round of offers
        self.agents_by_type[University].do("offer")
        # Students accept the best enrollment offer
        self.agents_by_type[Student].do("accept")
        # Universities with remaining capacity extend offers to students who
        # have not yet received any
        self.agents_by_type[University].do("waitlist")
        # Students from this second-round of offers accept the best offer
        self.agents_by_type[Student].do("accept")
        # University attributes are updated to reflect the new student body
        self.agents_by_type[University].do("update_prestige")
    # I still still need to implement stopping conditions for the model as well as data-collection for batch runs