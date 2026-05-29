## Use numpy to represent vectors as arrays
import numpy as np
## Using experimental continuous space implementation
from mesa.experimental.continuous_space import ContinuousSpaceAgent

class Student(ContinuousSpaceAgent):
    ## Student agents are initialized with wealth, merit, and information
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
        # Merit is fit to within the merit_window
        ideal_min = wealth - (self.model.merit_window / 2)
        actual_min = max(0, min(1 - self.model.merit_window, ideal_min))
        self.merit = merit * self.model.merit_window + actual_min
        
        self.offers = []
        self.decision = None
        self.label = 'S'
        # Student information is determined by the parameter and, if applicable,
        # randomly assigned
        if self.model.information == "No information":
            self.information = False
        elif self.model.information == "Perfect information":
            self.information = True
        else:
            self.information = self.model.rng.random() > 0.5

    def accept(self):
        # Students consider all offers and choose the highest utility offer
        if not self.offers or self.decision:
            return
        best_offer = (None, 0)
        for offer in self.offers:
            # If students are assigned to have financial information, they
            # cancluate tuition based on their actual paid amount rather than
            # the university sticker price.
            if self.information:
                perceived_tuition = min(self.wealth, offer.tuition)
            else:
                perceived_tuition = offer.tuition
            offer_utility = offer.prestige / (perceived_tuition / self.wealth)
            if offer_utility > best_offer[1]:
                best_offer = (offer, offer_utility)
        
        self.decision = best_offer[0]
        best_offer[0].acceptances += 1
        best_offer[0].total_revenue += min(self.wealth, best_offer[0].tuition)
        self.position = (self.wealth,
                         best_offer[0].position[1]+self.model.rng.uniform(-0.05, 0.05))
    
    def reset(self):
        # After each step, students reset to having no offers and no decision.
        # Students could also re-calculate their merit and wealth values if desired
        #self.merit = self.model.rng.uniform(0,1)
        #self.wealth = self.model.rng.uniform(0,1)
        self.offers = []
        self.decision = None

class University(ContinuousSpaceAgent):
    ## University agents are initialized with tuition and prestige.
    # Currently prestige and tuition are initialized as the same value, but this
    # can be adjusted.
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
        # Universities send offers to the students with the highest incentive score
        ranked_student_list = []
        offer_count = 0
        # Student expected revenues are calculated
        for student in self.model.agents_by_type[Student]:
            expected_revenue = min(student.wealth, self.tuition) + student.merit * self.prestige * self.model.donate
            score = expected_revenue * self.model.incentive + student.merit * (1-self.model.incentive)
            ranked_student_list.append((score, student.merit, student))
            
        ranked_student_list.sort(reverse=True)
        i = 0
        # Until the capacity is reached, students are sent offers in order of
        # expected revenue
        while offer_count < self.model.capacity:
            ranked_student_list[i][2].offers.append(self)
            i += 1
            offer_count += 1
    
    def waitlist(self):
        # Students who did not yet receive offers are re-considered for admission
        # by universities with remaining capacity
        available_students = []
        for student in self.model.agents_by_type[Student]:
            expected_revenue = min(student.wealth, self.tuition) + student.merit * self.prestige * self.model.donate
            score = expected_revenue * self.model.incentive + student.merit * (1-self.model.incentive)
            available_students.append((score, student.merit, student))
        available_students.sort(reverse=True)
        offers = self.acceptances
        i = 0
        while offers < self.model.capacity:
            available_students[i][2].offers.append(self)
            i += 1
            offers += 1
    


    def update_prestige(self):
        # Universities update their tuition and prestige based on student enrollment
        merit_list = [student.merit for student in self.model.agents_by_type[Student] if student.decision == self]
        # Prestige is re-calculated
        if not merit_list: # This is necessary for universities with no acceptances
            self.prestige = max(self.prestige-0.05, 0.1)
        else:
            new_prestige = np.mean(merit_list)
            self.prestige = self.prestige * 0.9 + new_prestige * 0.1
        # University tuition is re-calculated based on the number of acceptances
        if self.acceptances > self.model.capacity / self.model.university_count ** 2:
            self.tuition = min(self.tuition+0.05, 1)
        else:
            self.tuition = max(self.tuition-0.05, 0.1)
        self.position = (self.tuition, self.position[1])

    def reset(self):
        # Universities reset their number of students enrolled
        self.acceptances = 0
        self.total_revenue = 0
