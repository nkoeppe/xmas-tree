from effects.color_gradient_effect import ColorGradientSweepEffect
from effects.expanding_rings import ExpandingRingsEffect
from effects.four_plane_collision_effect import FourPlaneCollisionEffect
from effects.plain_sweep_effect import PlaneSweepEffect
from effects.plane_ripple_effect import PlainRippleEffect
from effects.random_effect import RandomEffect
from effects.twinkling_sparkle_effect import TwinklingSparkleEffect
from effects.two_plain_collision_effect import TwoPlainCollisionEffect
from effects.wave_3d_effect import Wave3DEffect

from registry.effect_registry import EffectRegistry
registered_effects = EffectRegistry.list_effects()
