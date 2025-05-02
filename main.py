import random
import pygame
from maps.map import Map, TILE_SIZE
from sim.src.model import CovidModel

SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 736
FPS = 15  # 60

# class Agent:
#     def __init__(self, x, y):
#         self.x = x
#         self.y = y
#         self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
#         self.color = (255, 0, 0)

#     def update(self, mapa):
#         keys = pygame.key.get_pressed()
#         dx, dy = 0, 0
#         if keys[pygame.K_LEFT]:
#             dx = -1
#         elif keys[pygame.K_RIGHT]:
#             dx = 1
#         elif keys[pygame.K_UP]:
#             dy = -1
#         elif keys[pygame.K_DOWN]:
#             dy = 1

#         new_x, new_y = self.x + dx, self.y + dy
#         if mapa.is_allowed(new_x, new_y):
#             self.x, self.y = new_x, new_y
#             self.rect.topleft = (self.x * TILE_SIZE, self.y * TILE_SIZE)

#         current_layers = mapa.get_current_layers(self.x, self.y)
#         print(f"Agent znajduje się w warstwach: {current_layers}")

#     def draw(self, surface):
#         pygame.draw.rect(surface, self.color, self.rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simulation of virus spread")
    clock = pygame.time.Clock()
    mapa = Map("maps/walkway_map.tmx")
    model = CovidModel(
        N=10,
        width=1440 // TILE_SIZE,
        height=736 // TILE_SIZE,
        map=mapa,
    )

    running = True
    i = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_c
                and pygame.key.get_mods() & pygame.KMOD_CTRL
            ):
                running = False
            elif (
                event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
            ):  # dev helpers
                mouse_x, mouse_y = event.pos
                grid_x = mouse_x // TILE_SIZE
                grid_y = mouse_y // TILE_SIZE
                print(f"Clicked tile coordinates: ({grid_x}, {grid_y})")
        model.step()
        screen.fill((0, 0, 0))
        mapa.draw_map()

        positions = model.datacollector.get_agent_vars_dataframe().xs(
            i + 1, level="Step"
        )

        x = [pos[0] for pos in positions["pos"]]
        y = [pos[1] for pos in positions["pos"]]

        for pos in zip(x, y):
            x, y = pos
            pygame.draw.circle(
                screen,
                (255, 0, 0),
                (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2),
                TILE_SIZE // 2,
            )
        print(model.agents[0].destination)
        pygame.display.update()
        i += 1
        clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    main()
