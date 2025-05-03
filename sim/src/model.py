import mesa
import mesa.datacollection

from maps.map import Map
from sim.src.generators import (
    DestinationGenerator,
    SpawnPointGenerator,
)
from sim.src.params import BuldingType
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

        for _ in range(self.num_agents):
            agent = agen.next()
            agent.respawn()
        self.datacollector = mesa.datacollection.DataCollector(
            agent_reporters={
                "pos": "pos",
            }
        )

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

    def step(self) -> None:
        self.datacollector.collect(self)
        for agent in self.agents:
            if isinstance(agent, HumanAgent):
                act = agent.determine_action()
                agent.step(act)
