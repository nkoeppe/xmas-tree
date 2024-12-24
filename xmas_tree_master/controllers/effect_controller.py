# controllers/effect_controller.py
import os
import json
from registry.effect_registry import EffectRegistry

class EffectController:
    """
    Manages LED effects and dynamically switches between them.
    """
    def __init__(self, controller):
        self.controller = controller

    def change_effect(self, effect_name, client_id=None, **kwargs):
        """
        Change the current effect.
        """
        effect_class = EffectRegistry.get_effect(effect_name)
        if not effect_class:
            raise ValueError(f"Unknown effect: {effect_name}")

        # Load saved defaults if available
        saved_config = self._load_saved_config(client_id, effect_name)
        merged_config = saved_config.copy()
        merged_config.update(kwargs)

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
            **merged_config
        )
        self.controller.set_effect(effect)
        print(f"Effect updated to: {effect_name}")

    def save_default_config(self, client_id, effect_name, config):
        """
        Saves new default config for the given client/effect.
        """
        directory = f"configs/{client_id}"
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, f"{effect_name}_default.json")
        with open(path, "w") as f:
            json.dump(config, f)
        print(f"Default config saved for {client_id}, effect {effect_name}")

    def _load_saved_config(self, client_id, effect_name):
        """
        Load any previously saved default config for this client and effect.
        """
        if not client_id:
            return {}
        path = f"configs/{client_id}/{effect_name}_default.json"
        if os.path.isfile(path):
            with open(path, "r") as f:
                return json.load(f)
        return {}
