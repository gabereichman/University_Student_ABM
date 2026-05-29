import numpy as np

from mesa import Model
from agents import Student
from agents import University
from mesa.experimental.continuous_space import ContinuousSpace
from mesa.datacollection import DataCollector

class UniversityRevenue(Model):
    ## Initialize model, including all relevant parameters. Inherit seed propety from parent class
    def __init__(
        self,
        student_count=1000,
        university_count=5,
        donate = 1,
        capacity_prop = .3,
        merit_window = 0,
        incentive = 1,
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
        self.university_count = university_count
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
        # The size of the window of possible merit values dependent on wealth
        self.merit_window = merit_window
        # The incentive weight of revenue vs. merit for universities
        self.incentive = incentive
        # The degree of financial information for students to hold
        self.information = information

        # Define data collector to collect model-level metrics
        self.datacollector = DataCollector(
            model_reporters={
                # 1. Average standard deviation of merit within each school
                "Merit_std": lambda m: np.mean([
                    np.std([s.merit for s in m.agents_by_type[Student] if s.decision == u])
                    for u in m.agents_by_type[University]
                    if any(s.decision == u for s in m.agents_by_type[Student])  # Only schools with enrolled students
                ]) if any(s.decision is not None for s in m.agents_by_type[Student]) else 0,
                
                # 2. Average standard deviation of wealth within each school
                "Wealth_std": lambda m: np.mean([
                    np.std([s.wealth for s in m.agents_by_type[Student] if s.decision == u])
                    for u in m.agents_by_type[University]
                    if any(s.decision == u for s in m.agents_by_type[Student])
                ]) if any(s.decision is not None for s in m.agents_by_type[Student]) else 0,
                
                # 3. Correlation between Tuition and Prestige
                "Tuition_Prestige_Corr": lambda m: np.corrcoef(
                    [u.tuition for u in m.agents_by_type[University]],
                    [u.prestige for u in m.agents_by_type[University]]
                )[0, 1] if len(m.agents_by_type[University]) > 1 else 0,
                
                # 4. Total Revenue across all universities combined
                "Total_Revenue": lambda m: sum(u.total_revenue for u in m.agents_by_type[University])
            }
        )

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

        self.datacollector.collect(self)

        max_tuition = max([university.tuition for university in self.agents_by_type[University]])
        # Stop when one university maximizes tuition
        if max_tuition == 1:
            self.running = False