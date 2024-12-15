from registry.effect_registry import EffectRegistry


def RegisterEffect():
    """
    Decorator to register an effect with a unique selector.
    """
    def decorator(effect_class):
        if not hasattr(effect_class, "effect_selector"):
            raise ValueError("Effect class must have an 'effect_selector' attribute.")

        EffectRegistry.register(effect_class.effect_selector, effect_class)
        return effect_class

    return decorator
