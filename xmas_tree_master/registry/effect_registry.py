# registry/effect_registry.py
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
        """
        Return a list of dicts, each containing 'selector', 'name', and 'default_config'.
        """
        results = []
        for selector, effect_cls in cls._registry.items():
            results.append({
                "selector": selector,
                "name": getattr(effect_cls, "name", selector),
                "default_config": effect_cls.default_config
            })
        return results
