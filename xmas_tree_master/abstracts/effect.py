from abc import ABC, abstractmethod

from decoratos.register_effect import RegisterEffect


class Effect(ABC):
    """
    Abstract base class for LED effects.
    Each effect defines how to update the colors of the LEDs.
    """

    def __init__(self, pixels, coords, **kwargs):
        """
        Initialize the effect.
        :param pixels: A mutable list or object that represents the current LED colors.
        :param coords: A list of 3D coordinates for each LED.
        :param kwargs: Additional configuration parameters for the effect.
        """
        self.pixels = pixels
        self.coords = coords
        self.config = kwargs

    @abstractmethod
    def update(self):
        """
        Update the LED colors for one frame of the effect.
        This method should be overridden by subclasses.
        """
        pass
