from typing import Optional
import mesa
import mesa.datacollection
import random


from maps.map import Map
from sim.src.generators import (
    DestinationGenerator,
    SpawnPointGenerator,
)
from sim.src.params import BuldingType, IllnessStates
from .agents import (
    HumanAgent,
    HumanAgentGenerator,
)


class CovidModel(mesa.Model):
    """
    Model class for the COVID-19 simulation.
    This class is responsible for managing the simulation environment,
    including the grid, agents, and data collection.
    """

    def __init__(self, N, width, height, map: Map):
        """
        Create a new model with the given parameters.
        Args:
            N: Number of agents
            width: Width of the grid
            height: Height of the grid
            map: Map object containing the layers and positions
        """

        super().__init__()
        self.width = width
        self.height = height
        self.num_agents = N
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.map = map
        self.__init_buildings(self.map)
        self.destgen = DestinationGenerator(self.buildings)

        spawngen = SpawnPointGenerator(
            houses=self.buildings[BuldingType.HOUSE],
        )
        agen = HumanAgentGenerator(self, spawngen)

        self.custom_agents = []
        for _ in range(self.num_agents):
            agent = agen.next()
            agent.respawn()
            self.custom_agents.append(agent)

        self.datacollector = mesa.datacollection.DataCollector(
            agent_reporters={
                "pos": "pos",
            }
        )
        self.grid.add_property_layer(
            mesa.space.PropertyLayer(
                "Virus",
                self.width,
                self.height,
                0.0,
                float,
            ),
        )

        self.steps_elapsed = 0
        self.patient_zero_infected = False

    def __init_buildings(self, map: Map):
        """
        Initialize the buildings on the map.
        Args:
            map: Map object containing the layers and positions
        """

        self.buildings: dict[BuldingType, list[tuple]] = {}
        houses = map.get_layer_positions_normalized("houses")
        fastfood = map.get_layer_positions_normalized("fastfood")
        library = map.get_layer_positions_normalized("library")
        shop = map.get_layer_positions_normalized("shop")
        hospital = map.get_layer_positions_normalized("hospital")
        self.buildings[BuldingType.HOSPITAL] = hospital
        self.buildings[BuldingType.HOUSE] = houses
        self.buildings[BuldingType.FASTFOOD] = fastfood
        self.buildings[BuldingType.LIBRARY] = library
        self.buildings[BuldingType.SHOP] = shop

    def building_at_pos(self, pos: tuple[int, int]) -> Optional[BuldingType]:
        for type_, list_ in self.buildings.items():
            if pos in list_:
                return type_
        return None

    def step(self) -> None:

        self.steps_elapsed += 1

        # Infect patient zero after ~5 seconds (e.g., 300 steps at ~16ms intervals)
        if not self.patient_zero_infected and self.steps_elapsed >= 100:
            eligible = [a for a in self.custom_agents if not a.face_cover]
            if eligible:
                patient_zero = random.choice(eligible)
                patient_zero.status = IllnessStates.INFECTED
                self.patient_zero_infected = True
                print(f"Patient zero infected at step {self.steps_elapsed}")

        self.datacollector.collect(self)
        for agent in self.custom_agents:

            if isinstance(agent, HumanAgent):
                act = agent.determine_action()
                agent.step(act)
                if agent.status == IllnessStates.INFECTED:
                    # leave some virus on the ground
                    virus: mesa.space.PropertyLayer = self.grid.properties["Virus"]
                    virus.set_cell(agent.pos, virus.data[agent.pos] + (1 if agent.face_cover else 10))
        # Zanikanie wirusa na wszystkich płytkach
        virus: mesa.space.PropertyLayer = self.grid.properties["Virus"]
        if self.steps_elapsed % 5 == 0:
            virus: mesa.space.PropertyLayer = self.grid.properties["Virus"]
            for x in range(self.width):
                for y in range(self.height):
                    current_level = virus.data[(x, y)]
                    new_level = max(0.0, current_level - 1)
                    virus.set_cell((x, y), new_level)
