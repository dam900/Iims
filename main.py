import pygame
from maps.map import Map, TILE_SIZE

SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 736
FPS = 60

class Agent:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.color = (255, 0, 0)

    def update(self, mapa):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -1
        elif keys[pygame.K_RIGHT]:
            dx = 1
        elif keys[pygame.K_UP]:
            dy = -1
        elif keys[pygame.K_DOWN]:
            dy = 1

        new_x, new_y = self.x + dx, self.y + dy
        if mapa.is_allowed(new_x, new_y):
            self.x, self.y = new_x, new_y
            self.rect.topleft = (self.x * TILE_SIZE, self.y * TILE_SIZE)

        current_layers = mapa.get_current_layers(self.x, self.y)
        print(f"Agent znajduje się w warstwach: {current_layers}")

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simulation of virus spread")
    clock = pygame.time.Clock()
    mapa = Map("maps/walkway_map.tmx")
    agent = Agent(0, 0)

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((0, 0, 0))
        mapa.draw_map()
        agent.update(mapa)
        agent.draw(screen)
        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()

if __name__ == "__main__":
    main()
