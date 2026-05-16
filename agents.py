## Use numpy to represent vectors as arrays
import numpy as np
## Using experimental continuous space implementation
from mesa.experimental.continuous_space import ContinuousSpaceAgent

class Student(ContinuousSpaceAgent):
    ## Define initiation. Inherit space and model properties from parent class
    def __init__(
        self,
        model,
        space,
        position=(0,0),
        wealth = 1,
        merit = 1,
    ):
        ## Initialize parameters
        super().__init__(space, model)
        self.position = position
        self.wealth = wealth
        self.merit = merit
        self.offers = []
        self.decision = None
        self.label = 'S'
        if self.model.information == "No information":
            self.information = False
        elif self.model.information == "Perfect information":
            self.information = True
        else:
            self.information = self.model.rng.random() > 0.5

    def accept(self):
        if not self.offers or self.decision:
            return
        best_offer = (None, 0)
        for offer in self.offers:
            if self.information:
                real_tuition = min(self.wealth, offer.tuition)
            else:
                real_tuition = offer.tuition
            offer_utility = offer.prestige / (real_tuition / self.wealth)
            if offer_utility > best_offer[1]:
                best_offer = (offer, offer_utility)
        
        self.decision = best_offer[0]
        best_offer[0].acceptances += 1
        best_offer[0].total_revenue += min(self.wealth, best_offer[0].tuition)
        self.position = (self.wealth,
                         best_offer[0].position[1]+self.model.rng.uniform(-0.05, 0.05))
    
    def reset(self):
        #self.merit = self.model.rng.uniform(0,1)
        #self.wealth = self.model.rng.uniform(0,1)
        self.offers = []
        self.decision = None

class University(ContinuousSpaceAgent):
    def __init__(
            self,
            model,
            space,
            position=(0,0),
            tuition=.5,
            prestige=1
    ):
        super().__init__(space, model)
        self.position = (prestige, position[1])
        self.tuition = prestige
        self.prestige = prestige
        self.acceptances = 0
        self.label = 'U'
        self.total_revenue = 0

    def offer(self):
        ranked_student_list = []
        offer_count = 0
        for student in self.model.agents_by_type[Student]:
            expected_revenue = min(student.wealth, self.tuition) + student.merit * self.prestige * self.model.donate
            if (student.merit > self.prestige and student.wealth > self.tuition):
                student.offers.append(self)
                offer_count += 1
            else:
                ranked_student_list.append((expected_revenue, student.merit, student))
            
        ranked_student_list.sort()
        i = 0
        while offer_count < self.model.capacity:
            ranked_student_list[i][2].offers.append(self)
            i += 1
            offer_count += 1
    
    def waitlist(self):
        available_students = []
        for student in self.model.agents_by_type[Student]:
            expected_revenue = min(student.wealth, self.tuition) + student.merit * self.prestige * self.model.donate
            available_students.append((expected_revenue, student.merit, student))
        available_students.sort()
        offers = self.acceptances
        i = 0
        while offers < self.model.capacity:
            available_students[i][2].offers.append(self)
            i += 1
            offers += 1
    


    def update_prestige(self):
        
        merit_list = [student.merit for student in self.model.agents_by_type[Student] if student.decision == self]
        if not merit_list:
            self.prestige = max(self.prestige-0.05, 0.1)
        new_prestige = np.mean(merit_list)
        if self.prestige < new_prestige:
            self.tuition = min(self.tuition+0.05, 1)
        else:
            self.tuition = max(self.tuition-0.1, 0.1)
        if merit_list:
            self.prestige = self.prestige * 0.75 + new_prestige * 0.25
        self.position = (self.tuition, self.position[1])

    def reset(self):
        self.acceptances = 0
