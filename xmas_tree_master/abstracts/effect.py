from abc import ABC, abstractmethod



class Effect(ABC):
    """
    Abstract base class for LED effects.
    Each effect defines how to update the colors of the LEDs.
    """
    def __init__(self, **kwargs):
        """
        Initialize the effect.
        :param pixels: A mutable list or object that represents the current LED colors.
        :param coords: A list of 3D coordinates for each LED.
        :param kwargs: Additional configuration parameters for the effect.
        """
        print(f"Initializing effect {type(self).__name__}")
        self.config = kwargs

        self.pixels = self.config['pixels']
        self.coords = self.config['coords']
        self.min_y = self.config['min_y']
        self.max_y = self.config['max_y']
        self.min_x = self.config['min_x']
        self.max_x = self.config['max_x']
        self.min_z = self.config['min_z']
        self.max_z = self.config['max_z']
        self.center = self.config['center']

    @property
    @abstractmethod
    def default_config(self):
        pass


    @abstractmethod
    def update(self):
        """
        Update the LED colors for one frame of the effect.
        This method should be overridden by subclasses.
        """
        pass

    def get_config(self, key, parser):
        """
        Update the LED colors for one frame of the effect.
        This method should be overridden by subclasses.
        """
        return parser(self.config[key]) if key in self.config else self.default_config[key]
