from __future__ import annotations
import random
from typing import Optional
import mesa

from enum import Enum, auto

from pygame import Surface
import pygame

from maps.map import Map


class BuldingType(Enum):
    """
    Building types present in the simulation.
    """

    SHOP = "shop"
    HOUSE = "house"
    LIBRARY = "library"
    FASTFOOD = "fastfood"
    HOSPITAL = "hospital"


class IllnessStates(Enum):
    """
    Illness states of the agent.
    """

    SUSCEPTIBLE = auto()
    INFECTED = auto()
    RECOVERED = auto()


class SocialDistancingStates(Enum):
    """
    Social distancing options.
    """

    NO_SOCIAL_DISTANCING = auto()
    AVERAGE_SOCIAL_DISTANCING = auto()
    NORMAL_SOCIAL_DISTANCING = auto()
    EXTREME_SOCIAL_DISTANCING = auto()


class AgeGroups(Enum):
    """
    Age groups that the agent is a part of.
    """

    CHILD = auto()
    YOUNG = auto()
    ADULT = auto()
    ELDERLY = auto()


class ActivityLikelihoods(Enum):
    """
    Wheter the agent will go out a lot or stay at home.
    """

    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()


class HumanAgentActions(Enum):
    """
    Actions that the agent can take.
    """

    STAY_IN_PLACE = auto()
    MOVE = auto()


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
        self.prev_pos: Optional[tuple[int, int]] = self.home
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
        if self.is_moving:
            # if the agent is already moving, continue moving
            # until destination is reached
            best_pos = self.path.pop(0)

            self.grid.move_agent(
                self,
                (
                    best_pos[0],
                    best_pos[1],
                ),
            )
            self.prev_pos = self.pos
            if self.pos == self.destination:
                self.is_moving = False
                self.destination = None
                self.prev_pos = None
            return
        if action == HumanAgentActions.STAY_IN_PLACE:
            # if the agent chose to stay in place, dont do anything
            self.is_moving = False
            self.destination = None
            self.prev_pos = None
        elif action == HumanAgentActions.MOVE:
            # if the agent chose to move set the destination
            self._set_destination(self.model.destgen.next(self))
            self.is_moving = True
        else:
            raise ValueError(f"Unknown action: {action}")

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
        +----------------+----------------+----------------+
        | Activity       | Low            | Medium         | High           |
        +----------------+----------------+----------------+
        | Move           | 20%            | 50%            | 80%            |
        | Stay in place  | 80%            | 50%            | 20%            |
        +----------------+----------------+----------------+
        """

        match move_likelihood:
            case ActivityLikelihoods.LOW:
                # 80% stay in place, 20% move
                return [HumanAgentActions.STAY_IN_PLACE for _ in range(8)] + [
                    HumanAgentActions.MOVE for _ in range(2)
                ]
            case ActivityLikelihoods.MEDIUM:
                # 50% stay in place, 50% move
                return [HumanAgentActions.STAY_IN_PLACE for _ in range(5)] + [
                    HumanAgentActions.MOVE for _ in range(5)
                ]
            case ActivityLikelihoods.HIGH:
                # 20% stay in place, 80% move
                return [HumanAgentActions.STAY_IN_PLACE for _ in range(2)] + [
                    HumanAgentActions.MOVE for _ in range(8)
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


class SpawnPointGenerator:
    """
    A generator for spawn points.
    The generator generates spawn points for the agents.
    """

    def __init__(
        self,
        houses=list[tuple[int, int]],
    ):
        """
        Args:
            houses (list[tuple[int, int]]): The list of houses.
        """
        self.houses: list[tuple[int, int]] = houses

    def next(self) -> tuple:
        return random.choice(self.houses)


class DestinationGenerator:
    """
    A generator for destinations.
    The generator generates destinations for the agents
    based on their parameters.
    """

    def __init__(
        self,
        buildings: dict[BuldingType, list[tuple[int, int]]],
    ):
        """
        Args:
            buildings (dict[BuldingType, list[tuple[int, int]]]): The list of buildings.
        """
        self.buildings: dict[BuldingType, list[tuple[int, int]]] = buildings

    def _determine_building_type(self, agent: HumanAgent) -> BuldingType:
        if agent.status == IllnessStates.INFECTED:
            return BuldingType.HOSPITAL
        if not agent.is_home():
            return BuldingType.HOUSE
        return random.choice(
            [
                BuldingType.SHOP,
                BuldingType.LIBRARY,
                BuldingType.FASTFOOD,
            ]
        )

    def _get_destination(self, building_type: BuldingType, agent: HumanAgent) -> tuple:
        if building_type == BuldingType.HOUSE:
            return agent.home
        return random.choice(self.buildings[building_type])

    def next(self, agent: HumanAgent) -> tuple:
        building_type = self._determine_building_type(agent)
        return self._get_destination(building_type, agent)


class DestinationPathFinder:
    """
    A path finder for the agent.
    The path finder finds the path from the start position to the end position.
    The path is found using a breadth-first search algorithm.
    """

    def __init__(self, grid: mesa.space.MultiGrid, map: Map):
        """
        Args:
            grid (mesa.space.MultiGrid): The grid that the agent is a part of.
            map (Map): The map that the agent is a part of.
        """
        self.grid = grid
        self.map = map

    def _available_moves(self, pos: tuple[int, int]) -> list[tuple[int, int]]:
        adjecent = self.grid.get_neighborhood(
            pos,
            moore=False,
            include_center=False,
        )
        return list(filter(self.map.is_allowed, adjecent))

    def _find(
        self, start: tuple[int, int], end: tuple[int, int]
    ) -> list[tuple[int, int]]:
        queue = [(start, [start])]
        visited = set()

        while queue:
            current_pos, path = queue.pop(0)
            if current_pos == end:
                return path

            for next_pos in self._available_moves(current_pos):
                if next_pos not in visited:
                    visited.add(next_pos)
                    queue.append((next_pos, path + [next_pos]))

        return []

    def find(
        self, start: tuple[int, int], end: tuple[int, int]
    ) -> list[tuple[int, int]]:
        return self._find(start, end)
