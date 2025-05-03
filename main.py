import pygame
from maps.map import Map, TILE_SIZE
from sim.src.agents import HumanAgent
from sim.src.model import CovidModel

SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 736
FPS = 30  # 60


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simulation of virus spread")
    clock = pygame.time.Clock()
    mapa = Map("maps/walkway_map.tmx")
    model = CovidModel(
        N=100,
        width=1440 // TILE_SIZE,
        height=736 // TILE_SIZE,
        map=mapa,
    )

    running = True
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
        for agent in model.agents:
            if isinstance(agent, HumanAgent):
                agent.render(screen, TILE_SIZE, TILE_SIZE, TILE_SIZE // 2)

        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    main()
