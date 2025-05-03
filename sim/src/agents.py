from __future__ import annotations
import random
from typing import Optional
import mesa

from pygame import Surface
import pygame

from sim.src.generators import DestinationPathFinder, SpawnPointGenerator
from sim.src.params import (
    ActivityLikelihoods,
    AgeGroups,
    HumanAgentActions,
    IllnessStates,
    SocialDistancingStates,
)


class HumanAgent(mesa.Agent):
    """
    A human agent in the simulation.
    The agent has a status, face cover, social distance, age, and activity likelihood.
    The agent can move around the grid and interact with other agents.
    """

    def __init__(
        self,
        model: mesa.Model,
        status: IllnessStates = IllnessStates.SUSCEPTIBLE,
        face_cover: bool = False,
        social_distance: SocialDistancingStates = SocialDistancingStates.NO_SOCIAL_DISTANCING,
        age: int = 20,
        vaccinated: bool = False,
        active: ActivityLikelihoods = ActivityLikelihoods.MEDIUM,
        home: tuple[int, int] = (0, 0),
    ):
        """
        Args:
            model (mesa.Model): The model that the agent is a part of.
            status (IllnessStates): The illness state of the agent.
            face_cover (bool): Whether the agent is wearing a face cover.
            social_distance (SocialDistancingStates): The social distancing state of the agent.
            age (int): The age of the agent.
            vaccinated (bool): Whether the agent is vaccinated.
            active (ActivityLikelihoods): The activity likelihood of the agent.
            home (tuple[int, int]): The home position of the agent.
        """

        super().__init__(model)
        # settable params
        self.status = status
        self.face_cover = face_cover
        self.social_distance = social_distance
        self.vaccinated = vaccinated
        self.age = age
        self.active = active
        # illness params
        self.infection_time = 0
        self.likelihood_of_infection = 0.0
        self.likelihood_of_recovery = 0.0
        self.likelihood_of_death = 0.0

        # unsettable params
        self.age_group = HumanAgent.determine_age_group(age)
        self.move_likelihood_table = HumanAgent.determine_likelihood_of_mooving(
            active,
        )

        # simulation helpers
        self.home = home
        self.destination: Optional[tuple[int, int]] = None
        self.is_moving = False

        # pathfinding
        self.grid: mesa.space.MultiGrid = self.model.grid
        self.path_finder = DestinationPathFinder(self.grid, self.model.map)

        # rendering
        self.radius = random.randrange(5, 10, 1) / 10
        self.color = (
            random.randint(0, 128),
            random.randint(0, 128),
            random.randint(0, 128),
        )

    def respawn(self) -> None:
        """
        Respawn the agent at its home position.
        """
        self.grid.place_agent(self, self.home)

    def determine_action(self) -> HumanAgentActions:
        """
        Determine the action that the agent will take.
        """
        return random.choice(self.move_likelihood_table)

    def is_home(self) -> bool:
        """
        Check if the agent is at home.
        """
        return self.pos == self.home

    def _set_destination(self, dest) -> None:
        self.destination = dest
        self.path = self.path_finder.find(self.pos, dest)

    def step(self, action: HumanAgentActions) -> None:
        """
        Perform the action that the agent will take.
        The agent can either move to a new destination or stay in place.
        If the agent is already moving, it will continue to move to the next position in the path.
        If the agent reaches its destination, it will stop moving.

        This is the main function where all the logic of the agent is executed.
        """

        # actions realted to movement, order matters
        if self.is_moving:
            # if the agent is already moving, continue moving
            # until destination is reached
            new_x, new_y = self.path.pop(0)
            self.grid.move_agent(
                self,
                (new_x, new_y),
            )
            if self.pos == self.destination:
                self._on_destination_reached()
        elif action == HumanAgentActions.STAY_IN_PLACE:
            # if the agent chose to stay in place, dont do anything
            self._on_stay_in_place()
        elif action == HumanAgentActions.GO_OUT:
            # if the agent chose to move set the destination
            self._on_go_out()
        else:
            raise ValueError(f"Unknown action: {action}")

        if self.status == IllnessStates.INFECTED:
            ...  # do something here

    def _on_stay_in_place(self):
        self.is_moving = False
        self.destination = None

    def _on_go_out(self):
        self._set_destination(self.model.destgen.next(self))
        self.is_moving = True

    def _on_destination_reached(self):
        self.is_moving = False
        self.destination = None

    def render(self, surface: Surface, scale_x, scale_y, scale_r) -> None:
        """Render the agent on the screen."""
        x, y = self.pos
        pygame.draw.circle(
            surface,
            self.color,
            (x * scale_x + scale_x // 2, y * scale_y + scale_y // 2),
            self.radius * scale_r,
        )
        pass

    @classmethod
    def determine_likelihood_of_mooving(
        cls, move_likelihood: ActivityLikelihoods
    ) -> list[HumanAgentActions]:
        """
        Determine the likelihood of moving based on the activity likelihood.
        The likelihood is determined by the activity likelihood of the agent.
        The higher the activity likelihood, the more likely the agent is to move.

        The likelihood is determined by the following table:

        | Activity       | Move Likelihood | Stay in Place Likelihood |
        |----------------|-----------------|--------------------------|
        | Low            | 20%             | 80%                      |
        | Medium         | 50%             | 50%                      |
        | High           | 80%             | 20%                      |
        """

        match move_likelihood:
            case ActivityLikelihoods.LOW:
                # 80% stay in place, 20% move
                return [HumanAgentActions.STAY_IN_PLACE for _ in range(8)] + [
                    HumanAgentActions.GO_OUT for _ in range(2)
                ]
            case ActivityLikelihoods.MEDIUM:
                # 50% stay in place, 50% move
                return [HumanAgentActions.STAY_IN_PLACE for _ in range(5)] + [
                    HumanAgentActions.GO_OUT for _ in range(5)
                ]
            case ActivityLikelihoods.HIGH:
                # 20% stay in place, 80% move
                return [HumanAgentActions.STAY_IN_PLACE for _ in range(2)] + [
                    HumanAgentActions.GO_OUT for _ in range(8)
                ]
            case _:
                raise ValueError(f"Unknown activity likelihood: {move_likelihood}")

    @classmethod
    def determine_age_group(cls, age: int) -> AgeGroups:
        """
        Determine the age group of the agent based on the age.
        """
        if age < 18:
            return AgeGroups.CHILD
        elif age < 30:
            return AgeGroups.YOUNG
        elif age < 65:
            return AgeGroups.ADULT
        else:
            return AgeGroups.ELDERLY


class HumanAgentGenerator:
    """
    A generator for human agents.
    The generator generates agents with random attributes.
    """

    def __init__(
        self,
        model: mesa.Model,
        spawn_point_generator: SpawnPointGenerator,
    ):
        """
        Args:
            model (mesa.Model): The model that the agent is a part of.
            spawn_point_generator (SpawnPointGenerator): The spawn point generator.
        """

        self.model = model
        self.pos_generator = spawn_point_generator

    def next(self) -> HumanAgent:
        status = random.choice(list(IllnessStates))
        face_cover = random.choice([True, False])
        social_distance = random.choice(list(SocialDistancingStates))
        vaccinated = random.choice([True, False])
        age = random.randint(10, 100)
        active = random.choice(list(ActivityLikelihoods))
        home = self.pos_generator.next()

        return HumanAgent(
            model=self.model,
            status=status,
            face_cover=face_cover,
            social_distance=social_distance,
            vaccinated=vaccinated,
            age=age,
            active=active,
            home=home,
        )
