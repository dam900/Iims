from __future__ import annotations
import random
from typing import Optional
import mesa

from enum import Enum, auto


class IllnessStates(Enum):
    SUSCEPTIBLE = auto()
    INFECTED = auto()
    RECOVERED = auto()


class SocialDistancingStates(Enum):
    NO_SOCIAL_DISTANCING = auto()
    AVERAGE_SOCIAL_DISTANCING = auto()
    NORMAL_SOCIAL_DISTANCING = auto()
    EXTREME_SOCIAL_DISTANCING = auto()


class AgeGroups(Enum):
    CHILD = auto()
    YOUNG = auto()
    ADULT = auto()
    ELDERLY = auto()


class ActivityLikelihoods(Enum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()


class HumanAgentActions(Enum):
    STAY_IN_PLACE = auto()
    MOVE = auto()


class HumanAgent(mesa.Agent):
    def __init__(
        self,
        model: mesa.Model,
        status: IllnessStates = IllnessStates.SUSCEPTIBLE,
        face_cover: bool = False,
        social_distance: SocialDistancingStates = SocialDistancingStates.NO_SOCIAL_DISTANCING,
        age: int = 20,
        vaccinated: bool = False,
        active: ActivityLikelihoods = ActivityLikelihoods.MEDIUM,
    ):
        super().__init__(model)
        # settable params
        self.status = status
        self.face_cover = face_cover
        self.social_distance = social_distance
        self.vaccinated = vaccinated
        self.age = age
        self.active = active

        # unsettable params
        self.age_group = HumanAgent.determine_age_group(age)

        # illness params
        self.infection_time = 0
        self.likelihood_of_infection = 0.0
        self.likelihood_of_recovery = 0.0
        self.likelihood_of_death = 0.0
        
        self.move_likelihood_table = HumanAgent.determine_likelihood_of_mooving(active)
        
        self.destination: Optional[tuple[int, int]] = None
        self.is_moving = False

    def determine_action(self) -> HumanAgentActions:
        return random.choice(
            self.move_likelihood_table
        )
    
    def _set_destination(self) -> None:
        pass
    
    def step(self, action: HumanAgentActions ) -> None:
        """Only for testing purposes, what works and what doesn't"""
        if self.is_moving:
            #progress to that destination
            self.model.grid.move_agent(self, (self.pos[0] + random.randint(-5, 5), (self.pos[1] +random.randint(-5, 5))))
            if self.destination is not None:
                pass
            return
        if action == HumanAgentActions.STAY_IN_PLACE:
            self.is_moving = False
            self.destination = None
            pass
        elif action == HumanAgentActions.MOVE:
            # Determine a new destination
            self._set_destination()
            self.is_moving = True
            # new_x = self.pos[0] + random.choice([-1, 0, 1])
            # new_y = self.pos[1] + random.choice([-1, 0, 1])
            # self.model.grid.move_agent(self, (new_x, new_y))
        else:
            raise ValueError(f"Unknown action: {action}")

    @classmethod
    def determine_likelihood_of_mooving(cls, move_likelihood: ActivityLikelihoods) -> list[HumanAgentActions]:
        match move_likelihood:
            case ActivityLikelihoods.LOW:
                # 80% stay in place, 20% move
                return [HumanAgentActions.STAY_IN_PLACE for _ in range(8)] + [HumanAgentActions.MOVE for _ in range(2)]
            case ActivityLikelihoods.MEDIUM:
                # 50% stay in place, 50% move
                return [HumanAgentActions.STAY_IN_PLACE for _ in range(5)] + [HumanAgentActions.MOVE for _ in range(5)]
            case ActivityLikelihoods.HIGH:
                # 20% stay in place, 80% move
                return [HumanAgentActions.STAY_IN_PLACE for _ in range(2)] + [HumanAgentActions.MOVE for _ in range(8)]
            case _:
                raise ValueError(f"Unknown activity likelihood: {move_likelihood}")            

    @classmethod
    def determine_age_group(cls, age: int) -> AgeGroups:
        if age < 18:
            return AgeGroups.CHILD
        elif age < 30:
            return AgeGroups.YOUNG
        elif age < 65:
            return AgeGroups.ADULT
        else:
            return AgeGroups.ELDERLY


class HumanAgentGenerator:
    def __init__(self, model: mesa.Model):
        self.model = model

    def next(self) -> HumanAgent:
        status = random.choice(list(IllnessStates))
        face_cover = random.choice([True, False])
        social_distance = random.choice(list(SocialDistancingStates))
        vaccinated = random.choice([True, False])
        age = random.randint(10, 100)
        active = random.choice(list(ActivityLikelihoods))

        return HumanAgent(
            model=self.model,
            status=status,
            face_cover=face_cover,
            social_distance=social_distance,
            vaccinated=vaccinated,
            age=age,
            active=active,
        )


class SpawnPointGenerator:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def next(self) -> tuple:
        x = random.randrange(self.width)
        y = random.randrange(self.height)
        return (x, y)
