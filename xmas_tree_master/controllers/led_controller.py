import matplotlib.pyplot as plt
import threading
import time
import numpy as np
from queue import Queue, Empty


class LEDController:
    """
    Main controller class for managing LED effects and rendering.
    """

    def __init__(self, coords, pixel_count):
        """
        Initialize the controller.
        :param coords: A list of 3D coordinates for each LED.
        :param pixel_count: Total number of LEDs.
        """
        self.coords = coords
        self.pixels = [[0, 0, 0] for _ in range(pixel_count)]  # Initialize all LEDs to off
        self.effect = None
        self.running = False
        self.plot_queue = Queue()  # Thread-safe queue for updating plot

    def set_effect(self, effect):
        """
        Set the current effect.
        :param effect: An instance of the Effect subclass.
        """
        self.effect = effect

    def start(self):
        """
        Start the effect rendering loop.
        """
        self.running = True
        threading.Thread(target=self._render_effect, daemon=True).start()

    def stop(self):
        """
        Stop the rendering loop.
        """
        self.running = False

    def _render_effect(self):
        """
        Run the effect rendering loop and send updates to the plot queue.
        """
        while self.running and self.effect:
            self.effect.update()
            self.plot_queue.put(self.pixels)  # Send updated pixels to the plot
            time.sleep(0.05)  # Adjust for desired frame rate

    def get_plot_data(self):
        """
        Fetch the latest LED data for plotting.
        """
        try:
            # Non-blocking get for the latest pixel data
            return self.plot_queue.get_nowait()
        except Empty:
            return None  # No new data to update