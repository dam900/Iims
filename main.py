import pygame
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import numpy as np
from collections import deque
import threading
import time

from maps.map import Map, TILE_SIZE
from sim.src.agents import HumanAgent
from sim.src.model import CovidModel
from sim.src.params import IllnessStates

SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 736
FPS = 30

SCREEN_WIDTH_PLUS = SCREEN_WIDTH + 250


class SimulationAnalyzer:
    def __init__(self):
        self.data_history = {
            'susceptible': deque(maxlen=1000),
            'exposed': deque(maxlen=1000),
            'infected': deque(maxlen=1000),
            'recovered': deque(maxlen=1000),
            'dead': deque(maxlen=1000),
            'new_infections': deque(maxlen=1000),
            'cumulative_infections': deque(maxlen=1000),
            'cumulative_recoveries': deque(maxlen=1000),
            'cumulative_deaths': deque(maxlen=1000),
            'daily_deaths': deque(maxlen=1000),
            'reproduction_rate': deque(maxlen=1000)
        }

        self.total_infections = 0
        self.total_recoveries = 0
        self.total_deaths = 0
        self.prev_infected = 0
        self.prev_recovered = 0
        self.prev_dead = 0
        self.day_counter = 0
        self.steps_per_day = 30


        self.model_params = {
            'population': 200,
            'infection_rate': 0.7,
            'incubation_time': 5,
            'recovery_time': 14,
            'mortality_rate': 2.0
        }


        plt.style.use('seaborn-v0_8')
        self.setup_plots()

    def setup_plots(self):
        """Konfiguruje wykresy matplotlib"""
        self.fig, self.axes = plt.subplots(2, 2, figsize=(15, 10))
        self.fig.suptitle('📊 Analiza weryfikacyjna symulacji COVID-19', fontsize=16, fontweight='bold')


        self.ax_seir = self.axes[0, 0]
        self.ax_seir.set_title(' Model SEIR - Dynamika epidemii')
        self.ax_seir.set_xlabel('Dni')
        self.ax_seir.set_ylabel('Liczba osób')
        self.ax_seir.grid(True, alpha=0.3)


        self.ax_daily = self.axes[0, 1]
        self.ax_daily.set_title(' Nowe przypadki dziennie')
        self.ax_daily.set_xlabel('Dni')
        self.ax_daily.set_ylabel('Liczba przypadków')
        self.ax_daily.grid(True, alpha=0.3)


        self.ax_cumulative = self.axes[1, 0]
        self.ax_cumulative.set_title(' Przypadki kumulatywne')
        self.ax_cumulative.set_xlabel('Dni')
        self.ax_cumulative.set_ylabel('Liczba przypadków')
        self.ax_cumulative.grid(True, alpha=0.3)


        self.ax_mortality = self.axes[1, 1]
        self.ax_mortality.set_title(' Analiza śmiertelności')
        self.ax_mortality.set_xlabel('Dni')
        self.ax_mortality.set_ylabel('Liczba zgonów')
        self.ax_mortality.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.ion()

    def update_data(self, model, step_count):
        """Aktualizuje dane na podstawie stanu modelu"""

        if step_count % self.steps_per_day != 0:
            return

        self.day_counter += 1


        susceptible = sum(1 for a in model.agents if a.status == IllnessStates.SUSCEPTIBLE)
        infected = sum(1 for a in model.agents if a.status == IllnessStates.INFECTED)
        recovered = sum(1 for a in model.agents if a.status == IllnessStates.RECOVERED)
        dead = sum(1 for a in model.agents if a.status == IllnessStates.DEAD)


        new_infections = max(0, (infected + recovered + dead) - (
                    self.prev_infected + self.prev_recovered + self.prev_dead))
        new_recoveries = max(0, recovered - self.prev_recovered)
        new_deaths = max(0, dead - self.prev_dead)


        self.total_infections += new_infections
        self.total_recoveries += new_recoveries
        self.total_deaths += new_deaths


        if len(self.data_history['infected']) > 5:
            recent_infected = list(self.data_history['infected'])[-5:]
            if sum(recent_infected[:-1]) > 0:
                r_rate = sum(recent_infected[1:]) / sum(recent_infected[:-1])
            else:
                r_rate = 0
        else:
            r_rate = 1.5 if infected > 0 else 0


        self.data_history['susceptible'].append(susceptible)
        self.data_history['infected'].append(infected)
        self.data_history['recovered'].append(recovered)
        self.data_history['dead'].append(dead)
        self.data_history['new_infections'].append(new_infections)
        self.data_history['cumulative_infections'].append(self.total_infections)
        self.data_history['cumulative_recoveries'].append(self.total_recoveries)
        self.data_history['cumulative_deaths'].append(self.total_deaths)
        self.data_history['daily_deaths'].append(new_deaths)
        self.data_history['reproduction_rate'].append(r_rate)


        self.prev_infected = infected
        self.prev_recovered = recovered
        self.prev_dead = dead

        print(
            f"Dzień {self.day_counter}: S={susceptible}, I={infected}, R={recovered}, D={dead}, Nowe={new_infections}, R₀={r_rate:.2f}")

    def update_plots(self):
        """Aktualizuje wykresy"""
        if len(self.data_history['infected']) < 2:
            return

        days = list(range(len(self.data_history['infected'])))


        for ax in self.axes.flat:
            ax.clear()


        self.ax_seir = self.axes[0, 0]
        self.ax_seir.plot(days, list(self.data_history['susceptible']), 'g-', label='Podatni (S)', linewidth=2,
                          marker='o', markersize=3)
        self.ax_seir.plot(days, list(self.data_history['infected']), 'r-', label='Zarażeni (I)', linewidth=2,
                          marker='s', markersize=3)
        self.ax_seir.plot(days, list(self.data_history['recovered']), 'b-', label='Wyzdrowiali (R)', linewidth=2,
                          marker='^', markersize=3)
        self.ax_seir.plot(days, list(self.data_history['dead']), 'k-', label='Zmarli (D)', linewidth=2, marker='x',
                          markersize=3)
        self.ax_seir.set_title('🦠 Model SEIR - Dynamika epidemii')
        self.ax_seir.set_xlabel('Dni')
        self.ax_seir.set_ylabel('Liczba osób')
        self.ax_seir.legend()
        self.ax_seir.grid(True, alpha=0.3)


        self.ax_daily = self.axes[0, 1]
        if len(self.data_history['new_infections']) > 0:
            self.ax_daily.bar(days, list(self.data_history['new_infections']), alpha=0.7, color='red',
                              label='Nowe zarażenia', width=0.8)
        self.ax_daily.set_title('📈 Nowe przypadki dziennie')
        self.ax_daily.set_xlabel('Dni')
        self.ax_daily.set_ylabel('Liczba przypadków')
        self.ax_daily.legend()
        self.ax_daily.grid(True, alpha=0.3)


        self.ax_cumulative = self.axes[1, 0]
        self.ax_cumulative.plot(days, list(self.data_history['cumulative_infections']), 'r-',
                                label='Kumulatywne zarażenia', linewidth=3, marker='o', markersize=4)
        self.ax_cumulative.plot(days, list(self.data_history['cumulative_recoveries']), 'b-',
                                label='Kumulatywne wyzdrowienia', linewidth=3, marker='s', markersize=4)
        self.ax_cumulative.fill_between(days, list(self.data_history['cumulative_infections']), alpha=0.3, color='red')
        self.ax_cumulative.fill_between(days, list(self.data_history['cumulative_recoveries']), alpha=0.3, color='blue')
        self.ax_cumulative.set_title('📊 Przypadki kumulatywne')
        self.ax_cumulative.set_xlabel('Dni')
        self.ax_cumulative.set_ylabel('Liczba przypadków')
        self.ax_cumulative.legend()
        self.ax_cumulative.grid(True, alpha=0.3)


        self.ax_mortality = self.axes[1, 1]
        if len(self.data_history['daily_deaths']) > 0:
            self.ax_mortality.bar(days, list(self.data_history['daily_deaths']), alpha=0.7, color='black',
                                  label='Dzienne zgony', width=0.6)


        ax2 = self.ax_mortality.twinx()
        ax2.plot(days, list(self.data_history['reproduction_rate']), 'purple',
                 label='Współczynnik R₀', linewidth=2, marker='o', markersize=4)
        ax2.axhline(y=1, color='orange', linestyle='--', alpha=0.7, label='R₀ = 1')

        self.ax_mortality.set_title('⚰️ Analiza śmiertelności i R₀')
        self.ax_mortality.set_xlabel('Dni')
        self.ax_mortality.set_ylabel('Dzienne zgony', color='black')
        ax2.set_ylabel('Współczynnik R₀', color='purple')
        ax2.set_ylim(0, 3)


        lines1, labels1 = self.ax_mortality.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        self.ax_mortality.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        self.ax_mortality.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.draw()
        plt.pause(0.01)

    def print_statistics(self):
        """Wyświetla statystyki symulacji"""
        if len(self.data_history['infected']) == 0:
            return

        max_infected = max(self.data_history['infected']) if self.data_history['infected'] else 0
        peak_day = list(self.data_history['infected']).index(max_infected) if max_infected > 0 else 0
        total_infected = self.total_infections
        current_r = self.data_history['reproduction_rate'][-1] if self.data_history['reproduction_rate'] else 0
        total_deaths = self.total_deaths
        current_infected = self.data_history['infected'][-1] if self.data_history['infected'] else 0

        print(f"\n{'=' * 60}")
        print(f" STATYSTYKI SYMULACJI - DZIEŃ {self.day_counter}")
        print(f"{'=' * 60}")
        print(f" Szczyt zarażeń: {max_infected} osób (dzień {peak_day})")
        print(f" Obecnie zarażonych: {current_infected}")
        print(f" Łącznie zarażonych: {total_infected}")
        print(f" Łącznie zgonów: {total_deaths}")
        print(f" Aktualny R₀: {current_r:.2f}")
        print(
            f" Śmiertelność: {(total_deaths / total_infected * 100):.1f}%" if total_infected > 0 else "📊 Śmiertelność: 0%")
        print(f"{'=' * 60}")


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

    step_x = width / max_length if max_length > 1 else width
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
        points = []
        for i, val in enumerate(data):
            x = origin_x + i * step_x
            y = origin_y + height - val * scale_y
            points.append((x, y))

        if len(points) > 1:
            pygame.draw.lines(surface, colors.get(label, (0, 128, 0)), False, points, 3)

            for point in points:
                pygame.draw.circle(surface, colors.get(label, (0, 128, 0)), point, 2)

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
    pygame.display.set_caption("Simulation of virus spread - Advanced Analysis")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18, bold=True)


    analyzer = SimulationAnalyzer()

    mapa = Map("maps/walkway_map.tmx")
    model = CovidModel(
        N=200,
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
    step_count = 0

    print("🚀 Uruchomiono symulację z zaawansowaną analizą!")
    print("📊 Wykresy matplotlib będą aktualizowane co 30 kroków (1 dzień symulacji)")
    print("💡 Naciśnij 'P' aby wyświetlić statystyki")
    print("💡 Naciśnij 'S' aby zapisać wykresy")
    print("💡 Naciśnij 'R' aby zresetować symulację")

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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    analyzer.print_statistics()
                elif event.key == pygame.K_s:
                    plt.savefig(f'simulation_analysis_day_{analyzer.day_counter}.png', dpi=300, bbox_inches='tight')
                    print(f"💾 Zapisano wykresy jako 'simulation_analysis_day_{analyzer.day_counter}.png'")
                elif event.key == pygame.K_r:
                    analyzer = SimulationAnalyzer()
                    model = CovidModel(
                        N=200,
                        width=SCREEN_WIDTH // TILE_SIZE,
                        height=SCREEN_HEIGHT // TILE_SIZE,
                        map=mapa,
                    )
                    step_count = 0
                    infected_history.clear()
                    recovered_history.clear()
                    dead_history.clear()
                    cumulative_infections.clear()
                    cumulative_recoveries.clear()
                    print("🔄 Symulacja zresetowana!")
            elif (
                    event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
            ):
                mouse_x, mouse_y = event.pos
                grid_x = mouse_x // TILE_SIZE
                grid_y = mouse_y // TILE_SIZE
                print(f"Clicked tile coordinates: ({grid_x}, {grid_y})")

        model.step()
        step_count += 1


        analyzer.update_data(model, step_count)


        if step_count % analyzer.steps_per_day == 0:
            analyzer.update_plots()

        screen.fill((0, 0, 0))
        mapa.draw_map()

        for agent in model.agents:
            if isinstance(agent, HumanAgent):
                agent.render(screen, TILE_SIZE, TILE_SIZE, TILE_SIZE // 2)

        prop = model.grid.properties["Virus"]
        for i, row in enumerate(prop.data):
            for j, val in enumerate(row):
                if val > 0.0:
                    intensity = min(255, int(val))
                    overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    overlay.fill((255, 0, 0, intensity // 2))
                    screen.blit(overlay, (i * TILE_SIZE, j * TILE_SIZE))
                    draw_virus_progress_bar(screen, i, j, val, 3)


        sus = sum(1 for a in model.agents if a.status == IllnessStates.SUSCEPTIBLE)
        inf = sum(1 for a in model.agents if a.status == IllnessStates.INFECTED)
        rec = sum(1 for a in model.agents if a.status == IllnessStates.RECOVERED)
        ded = sum(1 for a in model.agents if a.status == IllnessStates.DEAD)


        infected_history.append(inf)
        recovered_history.append(rec)
        dead_history.append(ded)


        if not cumulative_infections:
            cumulative_infections.append(inf)
        else:

            total_affected = inf + rec + ded
            cumulative_infections.append(total_affected)

        if not cumulative_recoveries:
            cumulative_recoveries.append(rec)
        else:
            cumulative_recoveries.append(rec)


        label_x = SCREEN_WIDTH
        label_y = 0
        label_w = 250
        label_h = 140

        pygame.draw.rect(screen, (255, 255, 255), (label_x, label_y, label_w, label_h))

        screen.blit(font.render(f"Podatni: {sus}", True, (0, 128, 0)), (label_x + 10, label_y + 5))
        screen.blit(font.render(f"Zarażeni: {inf}", True, (255, 0, 0)), (label_x + 10, label_y + 25))
        screen.blit(font.render(f"Odporni: {rec}", True, (0, 0, 255)), (label_x + 10, label_y + 45))
        screen.blit(font.render(f"Zgony: {ded}", True, (0, 0, 0)), (label_x + 10, label_y + 65))


        current_r = analyzer.data_history['reproduction_rate'][-1] if analyzer.data_history['reproduction_rate'] else 0
        screen.blit(font.render(f"R₀: {current_r:.2f}", True, (128, 0, 128)), (label_x + 10, label_y + 85))
        screen.blit(font.render(f"Dzień: {analyzer.day_counter}", True, (0, 128, 0)), (label_x + 10, label_y + 105))
        screen.blit(font.render(f"Krok: {step_count}", True, (128, 128, 128)), (label_x + 10, label_y + 125))


        chart_x = SCREEN_WIDTH + 30
        chart_w = 200
        chart_h = 120


        recent_infected = infected_history[-100:] if len(infected_history) > 100 else infected_history
        recent_recovered = recovered_history[-100:] if len(recovered_history) > 100 else recovered_history
        recent_dead = dead_history[-100:] if len(dead_history) > 100 else dead_history
        recent_cum_inf = cumulative_infections[-100:] if len(cumulative_infections) > 100 else cumulative_infections
        recent_cum_rec = cumulative_recoveries[-100:] if len(cumulative_recoveries) > 100 else cumulative_recoveries

        draw_combined_chart(screen, {
            "Infected": recent_infected,
            "Recovered": recent_recovered,
            "Dead": recent_dead
        }, chart_x, SCREEN_HEIGHT - 600, chart_w, chart_h, font)

        draw_combined_chart(screen, {
            "Infected": recent_cum_inf
        }, chart_x, SCREEN_HEIGHT - 450, chart_w, chart_h, font, y_label="Kumulatywne zarażenia")

        draw_combined_chart(screen, {
            "Recovered": recent_cum_rec
        }, chart_x, SCREEN_HEIGHT - 300, chart_w, chart_h, font, y_label="Kumulatywne wyzdrowienia")

        pygame.display.update()
        clock.tick(FPS)


    analyzer.print_statistics()


    plt.savefig('final_simulation_analysis.png', dpi=300, bbox_inches='tight')
    print("💾 Zapisano końcowe wykresy jako 'final_simulation_analysis.png'")


    print("📊 Wykresy pozostaną otwarte. Zamknij je ręcznie.")
    plt.ioff()
    plt.show()

    pygame.quit()


if __name__ == "__main__":
    main()