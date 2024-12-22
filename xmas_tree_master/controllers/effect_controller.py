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
        effect = effect_class(
            pixels=self.controller.pixels,
            coords=self.controller.coords,
            min_y=self.controller.min_y,
            max_y=self.controller.max_y,
            min_x=self.controller.min_x,
            max_x=self.controller.max_x,
            min_z=self.controller.min_z,
            max_z=self.controller.max_z,
            center=self.controller.three_d_center,
            **kwargs
        )
        self.controller.set_effect(effect)
        print(f"Effect updated to: {effect_name}")
