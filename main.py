import pygame
from maps.map import Map, TILE_SIZE
from sim.src.agents import HumanAgent
from sim.src.model import CovidModel
from sim.src.params import IllnessStates


SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 736
FPS = 60  # 60

SCREEN_WIDTH_PLUS = SCREEN_WIDTH + 250

def draw_combined_chart(surface, data_dict, origin_x, origin_y, width, height, font, y_label="Liczba osób"):
    if all(len(data) == 0 for data in data_dict.values()):
        return

    pygame.draw.rect(surface, (255, 255, 255), (SCREEN_WIDTH, origin_y - 30, SCREEN_WIDTH_PLUS, height + 70))

    all_values = [val for data in data_dict.values() for val in data]
    max_val = max(all_values) if all_values else 1
    max_val = max(max_val, 1)

    data_lengths = [len(data) for data in data_dict.values()]
    max_length = max(data_lengths) if data_lengths else 1
    max_length = max(max_length, 1)

    step_x = width / max_length
    scale_y = height / max_val

    pygame.draw.line(surface, (0, 0, 0), (origin_x, origin_y + height), (origin_x + width, origin_y + height), 2)
    pygame.draw.line(surface, (0, 0, 0), (origin_x, origin_y), (origin_x, origin_y + height), 2)

    surface.blit(font.render(y_label, True, (0, 0, 0)), (origin_x - 5, origin_y - 25))
    surface.blit(font.render("Czas", True, (0, 0, 0)), (origin_x + width // 2 - 20, origin_y + height + 20))

    leftval = 25 if max_val > 9 else 20
    surface.blit(font.render("0", True, (0, 0, 0)), (origin_x - 20, origin_y + height - 10))
    surface.blit(font.render(str(max_val), True, (0, 0, 0)), (origin_x - leftval, origin_y - 10))
    surface.blit(font.render("0", True, (0, 0, 0)), (origin_x - 5, origin_y + height + 5))
    surface.blit(font.render(str(max_length), True, (0, 0, 0)), (origin_x + width - 25, origin_y + height + 5))

    colors = {
        "Infected": (255, 0, 0),
        "Recovered": (0, 0, 255),
        "Dead": (0, 0, 0)
    }

    for label, data in data_dict.items():
        if len(data) < 2:
            continue
        points = [
            (origin_x + i * step_x, origin_y + height - val * scale_y)
            for i, val in enumerate(data)
        ]
        pygame.draw.lines(surface, colors.get(label, (0, 128, 0)), False, points, 2)

    for label, data in data_dict.items():
        if not data:
            continue
        last_val = data[-1]
        leftval2 = 25 if last_val > 9 else 20
        y_pos = origin_y + height - last_val * scale_y
        color = colors.get(label, (0, 128, 0))
        text = font.render(str(last_val), True, color)
        surface.blit(text, (origin_x - leftval2, y_pos - 10))


def draw_virus_progress_bar(screen, i, j, val, thickness=2):
    pygame.draw.rect(
        screen,
        (0, 0, 0),
        pygame.Rect(
            i * TILE_SIZE,
            j * TILE_SIZE,
            TILE_SIZE,
            thickness,
        ),
    )
    pygame.draw.rect(
        screen,
        (255, 0, 0),
        pygame.Rect(
            i * TILE_SIZE,
            j * TILE_SIZE,
            min(TILE_SIZE, val / 255 * TILE_SIZE),
            thickness,
        ),
    )

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH_PLUS, SCREEN_HEIGHT))
    pygame.display.set_caption("Simulation of virus spread")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18, bold=True)  # Font do liczników
    mapa = Map("maps/walkway_map.tmx")
    model = CovidModel(
        N=30,
        width=SCREEN_WIDTH // TILE_SIZE,
        height=SCREEN_HEIGHT // TILE_SIZE,
        map=mapa,
    )

    virus_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    virus_surface.set_alpha(254 // 5)

    infected_history = []
    recovered_history = []
    dead_history = []
    cumulative_infections = []
    cumulative_recoveries = []

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

        prop = model.grid.properties["Virus"]
        for i, row in enumerate(prop.data):
            for j, val in enumerate(row):
                if val > 0.0:
                    intensity = min(255, int(val))  # ogranicz wartość do 0–255
                    overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    overlay.fill((255, 0, 0, intensity // 2))  # czerwona półprzezroczysta
                    screen.blit(overlay, (i * TILE_SIZE, j * TILE_SIZE))
                    draw_virus_progress_bar(screen, i, j, val, 3)

        # 🔢 Liczniki w prawym górnym rogu
        sus = sum(1 for a in model.agents if a.status == IllnessStates.SUSCEPTIBLE)
        inf = sum(1 for a in model.agents if a.status == IllnessStates.INFECTED)
        rec = sum(1 for a in model.agents if a.status == IllnessStates.RECOVERED)
        ded = sum(1 for a in model.agents if a.status == IllnessStates.DEAD)

        text_sus = font.render(f"Susceptible: {sus}", True, (0, 255, 0))
        text_inf = font.render(f"Infected: {inf}", True, (255, 0, 0))
        text_rec = font.render(f"Immune (rec): {rec}", True, (0, 0, 255))
        text_ded = font.render(f"Dead: {ded}", True, (0, 0, 0))

        paddingx = 30
        paddingy = 600
        bg_width = 160
        bg_height = 105
        bg_x =  paddingx
        bg_y = paddingy
        bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        bg_surface.fill((128, 128, 128, 160))  # szary, przezroczystość alpha=160 (0-255)
        # screen.blit(bg_surface, (bg_x, bg_y))
        # screen.blit(text_sus, (paddingx, paddingy)) #SCREEN_WIDTH - 300
        # screen.blit(text_inf, (paddingx, paddingy + 25))
        # screen.blit(text_rec, (paddingx, paddingy + 50))
        # screen.blit(text_ded, (paddingx, paddingy + 75))

        # Historia zarażeń (do wykresu)
        infected_history.append(inf)
        recovered_history.append(rec)
        dead_history.append(ded)

        if not cumulative_infections:
            cumulative_infections.append(inf)
        else:
            delta = max(0, inf - infected_history[-2]) if len(infected_history) > 1 else inf
            cumulative_infections.append(cumulative_infections[-1] + delta)

        if not cumulative_recoveries:
            cumulative_recoveries.append(rec)
        else:
            delta = max(0, rec - recovered_history[-2]) if len(recovered_history) > 1 else rec
            cumulative_recoveries.append(cumulative_recoveries[-1] + delta)

        # if len(infected_history) > 200:
        #    infected_history.pop(0)

        # Liczniki na samej górze po prawej stronie z białym tłem
        label_x = SCREEN_WIDTH
        label_y = 0
        label_w = 250
        label_h = 70

        pygame.draw.rect(screen, (255, 255, 255), (label_x, label_y, label_w, label_h))

        screen.blit(font.render(f"Zarażeni: {inf}", True, (255, 0, 0)), (label_x + 10, label_y + 5))
        screen.blit(font.render(f"Odporni: {rec}", True, (0, 0, 255)), (label_x + 10, label_y + 25))
        screen.blit(font.render(f"Zgony: {ded}", True, (0, 0, 0)), (label_x + 10, label_y + 45))


        # Rysuj wykres
        chart_x = SCREEN_WIDTH + 30
        chart_y = 20
        chart_w = 200
        chart_h = 150
        # 🔹 Wykres 1 – aktualne wartości
        draw_combined_chart(screen, {
            "Infected": infected_history,
            "Recovered": recovered_history,
            "Dead": dead_history
        }, chart_x, SCREEN_HEIGHT-634, chart_w, chart_h, font)

        # 🔹 Wykres 2 – kumulatywne przypadki zarażenia
        draw_combined_chart(screen, {
            "Infected": cumulative_infections
        }, chart_x, SCREEN_HEIGHT-412, chart_w, chart_h, font, y_label="Liczba zarażeń")

        draw_combined_chart(screen, {
            "Recovered": cumulative_recoveries
        }, chart_x, SCREEN_HEIGHT-190, chart_w, chart_h, font, y_label="Liczba wyzdrowień")

        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()




if __name__ == "__main__":
    main()
