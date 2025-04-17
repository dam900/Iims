import random
import mesa
import mesa.datacollection
from src.agents import HumanAgent, HumanAgentGenerator, SpawnPointGenerator


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

    def step(self) -> None:
        self.datacollector.collect(self)
        for agent in self.agents:
            if isinstance(agent, HumanAgent):
                act = agent.determine_action()
                agent.step(act)
                # self.grid.move_agent(agent, (agent.pos[0] + random.randint(-self.s, self.s), (agent.pos[1] +random.randint(-self.s, self.s))))
