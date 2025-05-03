from __future__ import annotations
import random
import mesa
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from sim.src.agents import HumanAgent


from maps.map import Map
from sim.src.params import BuldingType, IllnessStates


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

    def _determine_building_type(
        self,
        agent: HumanAgent,
    ) -> BuldingType:
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

    def _get_destination(
        self,
        building_type: BuldingType,
        agent: HumanAgent,
    ) -> tuple[int, int]:
        if building_type == BuldingType.HOUSE:
            return agent.home
        return random.choice(self.buildings[building_type])

    def next(self, agent) -> tuple:  #: HumanAgent,
        building_type = self._determine_building_type(agent)
        return self._get_destination(building_type, agent)


class DestinationPathFinder:
    """
    A path finder for the agent.
    The path finder finds the path from the start position to the end position.
    The path is found using a breadth-first search algorithm.
    """

    def __init__(
        self,
        grid: mesa.space.MultiGrid,
        map: Map,
    ):
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
