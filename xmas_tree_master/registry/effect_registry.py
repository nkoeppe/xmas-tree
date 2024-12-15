
class EffectRegistry:
    """
    Singleton registry for all effects.
    """
    _registry = {}

    @classmethod
    def register(cls, selector, effect_class):
        if selector in cls._registry:
            raise ValueError(f"Effect with selector '{selector}' is already registered.")
        cls._registry[selector] = effect_class

    @classmethod
    def get_effect(cls, selector):
        return cls._registry.get(selector, None)

    @classmethod
    def list_effects(cls):
        return list(cls._registry.keys())
