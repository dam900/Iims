from src.model import CovidModel
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np


def main():
    model = CovidModel(N=100, width=500, height=500)

    # Create figure and axis for animation
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, model.width)
    ax.set_ylim(0, model.height)
    ax.set_title("COVID-19 Agent Simulation")

    # Initialize scatter plot
    scatter = ax.scatter([], [], s=100, c="blue", marker="o")

    # Animation update function
    def update(frame):
        # Run the model step to collect data
        model.step()

        # Get the data for the current frame
        try:
            positions = model.datacollector.get_agent_vars_dataframe().xs(
                frame, level="Step"
            )

            # Extract x and y coordinates from positions
            x = [pos[0] for pos in positions["pos"]]
            y = [pos[1] for pos in positions["pos"]]

            scatter.set_offsets(np.column_stack([x, y]))
        except KeyError:
            # If no data is available for this frame, keep the previous positions
            pass

        return (scatter,)

    # Create animation
    ani = animation.FuncAnimation(fig, update, frames=10000, interval=16, blit=True)

    plt.show()


if __name__ == "__main__":
    main()
