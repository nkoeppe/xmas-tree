from registry.effect_registry import EffectRegistry

class EffectController:
    """
    Manages LED effects and dynamically switches between them.
    """
    def __init__(self, controller):
        self.controller = controller

    def change_effect(self, effect_name, **kwargs):
        """
        Change the current effect based on its name.
        """
        effect_class = EffectRegistry.get_effect(effect_name)
        if not effect_class:
            raise ValueError(f"Unknown effect: {effect_name}")
        effect = effect_class(self.controller.pixels, self.controller.coords, min_y=self.controller.min_y, max_y=self.controller.max_y,  **kwargs)
        self.controller.set_effect(effect)
        print(f"Effect updated to: {effect_name}")
