from enum import Enum
import mesa
import mesa.datacollection

from maps.map import Map
from .agents import HumanAgent, HumanAgentGenerator, SpawnPointGenerator


class BuldingType(Enum):
    SHOP = "shop"
    HOUSE = "house"
    LIBRARY = "library"
    FASTFOOD = "fastfood"
    HOSPITAL = "hospital"


class CovidModel(mesa.Model):
    def __init__(self, N, width, height):
        super().__init__()
        self.width = width
        self.height = height
        self.num_agents = N
        self.grid = mesa.space.MultiGrid(width, height, True)

        agen = HumanAgentGenerator(self)
        spawngen = SpawnPointGenerator(self.width, self.height)
        for _ in range(self.num_agents):
            agent = agen.next()
            pos = spawngen.next()
            self.grid.place_agent(agent, pos)
        self.datacollector = mesa.datacollection.DataCollector(
            agent_reporters={
                "pos": "pos",
            }
        )

    def __init_buildings(self, map: Map):
        self.buildings: dict[BuldingType, list[tuple]] = {}
        for building in BuldingType:
            self.buildings[building] = []
        self.buildings[BuldingType.HOSPITAL].append((0, 0))

    def step(self) -> None:
        self.datacollector.collect(self)
        for agent in self.agents:
            if isinstance(agent, HumanAgent):
                act = agent.determine_action()
                agent.step(act)
