from __future__ import annotations

from enum import Enum
from typing import Any, Callable, List, Optional, Union

import flet as ft
from flet.core.control import Control
from flet.core.control_event import ControlEvent
from flet.core.ref import Ref
from flet.core.types import ColorValue


# ── Enums ────────────────────────────────────────────────────────────────────

class ScrollDirection(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL   = "vertical"


class AnimateToCurve(Enum):
    LINEAR           = "linear"
    EASE_IN          = "easeIn"
    EASE_OUT         = "easeOut"
    EASE_IN_OUT      = "easeInOut"
    BOUNCE_IN        = "bounceIn"
    BOUNCE_OUT       = "bounceOut"
    ELASTIC_IN       = "elasticIn"
    ELASTIC_OUT      = "elasticOut"
    DECELERATE       = "decelerate"
    FAST_OUT_SLOW_IN = "fastOutSlowIn"


class EnlargeStrategy(Enum):
    """Maps to CenterPageEnlargeStrategy in carousel_slider."""
    SCALE  = "scale"
    HEIGHT = "height"
    ZOOM   = "zoom"


class ClipBehavior(Enum):
    NONE                     = "none"
    HARD_EDGE                = "hardEdge"
    ANTI_ALIAS               = "antiAlias"
    ANTI_ALIAS_WITH_SAVE_LAYER = "antiAliasWithSaveLayer"


class CarouselPageChangedReason(Enum):
    """Reason passed to on_change. Maps to CarouselPageChangedReason in Dart."""
    TIMED    = "timed"
    MANUAL   = "manual"
    CONTROLLER = "controller"


# ── Events ────────────────────────────────────────────────────────────────────

class CarouselChangeEvent(ControlEvent):
    """
    Fired when the page changes (on_change / onPageChanged).

    Attributes
    ----------
    index : int
        Zero-based index of the new page.
    reason : CarouselPageChangedReason
        Why the page changed: timed (autoplay), manual (swipe), or controller.
    """
    def __init__(self, e: ControlEvent):
        super().__init__(
            target=e.target, name=e.name,
            data=e.data, control=e.control, page=e.page,
        )
        parts = (e.data or "0:manual").split(":")
        self.index: int = int(parts[0])
        try:
            self.reason = CarouselPageChangedReason(parts[1])
        except ValueError:
            self.reason = CarouselPageChangedReason.MANUAL


class CarouselScrolledEvent(ControlEvent):
    """
    Fired continuously while scrolling (on_scrolled / onScrolled).

    Attributes
    ----------
    value : float
        Current scroll offset as a fraction of the page.
    """
    def __init__(self, e: ControlEvent):
        super().__init__(
            target=e.target, name=e.name,
            data=e.data, control=e.control, page=e.page,
        )
        self.value: float = float(e.data or 0.0)


# ── Main Control ──────────────────────────────────────────────────────────────

class Carousel(ft.Control):
    """
    Flet wrapper for the **carousel_slider 5.1.2** Flutter package.

    All ``CarouselOptions`` parameters are supported.

    Parameters
    ----------
    controls : list[Control]
        The carousel items (children).

    -- CarouselOptions --
    indicator_inactive_color: ColorValue
        The Color of the inactive indicator in the indicators list. Only take effect if enable indicator is ``True``
    indicator_active_color: ColorValue
        The Color of the active indicator in the indicators list. Only take effect if enable indicator is ``True``
    indicatorwidth: int
        Width of the indicator. Minimum Width should be atleast 110. Default ``None`` 
    enable_indicator : bool
        Enable/ Disable the Carousel indicator. Default ``True``
    disablegesture : bool
        Disable the CarouselSlider Gesture listening. Default ``False``.
    build_on_demand : bool
        Whether the controls should be built lazily to save memory and increase on performance. Default ``False``
    height : float | None
        Fixed height. When set, ``aspect_ratio`` is ignored.
    aspect_ratio : float
        Aspect ratio of the carousel. Default ``16/9``.
    viewport_fraction : float
        Fraction of the viewport each item occupies. Default ``0.8``.
    initial_page : int
        Page shown first. Default ``0``.
    enable_infinite_scroll : bool
        Loop items infinitely. Default ``True``.
    animate_to_closest : bool
        Animate to closest page on drag release. Default ``True``.
    reverse : bool
        Reverse scroll direction. Default ``False``.
    auto_play : bool
        Auto-advance pages. Default ``False``.
    auto_play_interval : int
        Milliseconds between auto-advances. Default ``4000``.
    auto_play_animation_duration : int
        Milliseconds for auto-play slide animation. Default ``800``.
    auto_play_curve : AnimateToCurve
        Curve for auto-play animation. Default ``FAST_OUT_SLOW_IN``.
    enlarge_center_page : bool
        Enlarge the centre page. Default ``False``.
    enlarge_strategy : EnlargeStrategy
        Strategy for centre-page enlargement. Default ``SCALE``.
    enlarge_factor : float
        Enlargement factor. Default ``0.3``.
    page_snapping : bool
        Snap to page boundaries. Default ``True``.
    scroll_direction : ScrollDirection
        Scroll axis. Default ``HORIZONTAL``.
    pause_auto_play_on_touch : bool
        Pause autoplay while user touches slider. Default ``True``.
    pause_auto_play_on_manual_navigate : bool
        Pause autoplay when controller methods are called. Default ``True``.
    pause_auto_play_in_finite_scroll : bool
        If infinite scroll is off, pause at last item. Default ``False``.
    disable_center : bool
        Don't wrap items in a Center widget. Default ``False``.
    pad_ends : bool
        Add padding so first/last items can be centred. Default ``True``.
    clip_behavior : ClipBehavior
        Clip behaviour of the slider. Default ``HARD_EDGE``.

    -- Events --
    on_change : Callable[[CarouselChangeEvent], None] | None
        Fired on every page change. ``event.index`` and ``event.reason``.
    on_scrolled : Callable[[CarouselScrolledEvent], None] | None
        Fired continuously while scrolling. ``event.value`` is scroll offset.

    -- Methods --
    next_page(duration, curve)
        Animate to the next page.
    previous_page(duration, curve)
        Animate to the previous page.
    jump_to_page(index)
        Instantly jump to a page (no animation).
    animate_to_page(index, duration, curve)
        Animate to a specific page index.
    """

    def __init__(
        self,
        controls: List[Control],
        # ── CarouselOptions ───────────────────────────────────────────
        height: Optional[float] = None,
        aspect_ratio: float = 16 / 9,
        viewport_fraction: float = 0.8,
        initial_page: int = 0,
        disablegesture: bool = False,
        enable_indicator: bool = True,
        indicatorwidth: int = None,
        indicator_inactive_color: ColorValue = None,
        indicator_active_color: ColorValue = None,
        build_on_demand: bool = False,
        enable_infinite_scroll: bool = True,
        animate_to_closest: bool = True,
        reverse: bool = False,
        auto_play: bool = False,
        auto_play_interval: int = 4000,
        auto_play_animation_duration: int = 800,
        auto_play_curve: AnimateToCurve = AnimateToCurve.FAST_OUT_SLOW_IN,
        enlarge_center_page: bool = False,
        enlarge_strategy: EnlargeStrategy = EnlargeStrategy.SCALE,
        enlarge_factor: float = 0.3,
        page_snapping: bool = True,
        scroll_direction: ScrollDirection = ScrollDirection.HORIZONTAL,
        pause_auto_play_on_touch: bool = True,
        pause_auto_play_on_manual_navigate: bool = True,
        pause_auto_play_in_finite_scroll: bool = False,
        disable_center: bool = False,
        pad_ends: bool = True,
        clip_behavior: ClipBehavior = ClipBehavior.HARD_EDGE,
        # ── Events ────────────────────────────────────────────────────
        on_change: Optional[Callable[[CarouselChangeEvent], None]] = None,
        on_scrolled: Optional[Callable[[CarouselScrolledEvent], None]] = None,
        # ── Base Control ──────────────────────────────────────────────
        ref: Optional[Ref] = None,
        visible: Optional[bool] = None,
        disabled: Optional[bool] = None,
        data: Any = None,
    ):
        super().__init__(ref=ref, visible=visible, disabled=disabled, data=data)

        self.controls                          = controls
        self.height                            = height
        self.aspect_ratio                      = aspect_ratio
        self.viewport_fraction                 = viewport_fraction
        self.initial_page                      = initial_page
        self.disablegesture                    = disablegesture
        self.enable_indicator                  = enable_indicator
        self.indicatorwidth                    = indicatorwidth
        self.indicator_active_color            = indicator_active_color
        self.indicator_inactive_color          = indicator_inactive_color
        self.build_on_demand                   = build_on_demand
        self.enable_infinite_scroll            = enable_infinite_scroll
        self.animate_to_closest                = animate_to_closest
        self.reverse                           = reverse
        self.auto_play                         = auto_play
        self.auto_play_interval                = auto_play_interval
        self.auto_play_animation_duration      = auto_play_animation_duration
        self.auto_play_curve                   = auto_play_curve
        self.enlarge_center_page               = enlarge_center_page
        self.enlarge_strategy                  = enlarge_strategy
        self.enlarge_factor                    = enlarge_factor
        self.page_snapping                     = page_snapping
        self.scroll_direction                  = scroll_direction
        self.pause_auto_play_on_touch          = pause_auto_play_on_touch
        self.pause_auto_play_on_manual_navigate = pause_auto_play_on_manual_navigate
        self.pause_auto_play_in_finite_scroll  = pause_auto_play_in_finite_scroll
        self.disable_center                    = disable_center
        self.pad_ends                          = pad_ends
        self.clip_behavior                     = clip_behavior
        self.on_change                         = on_change
        self.on_scrolled                       = on_scrolled

        # Internal ack handler for animate_to_page / next / previous / jump.
        # Counter appended to every command — makes each call unique so Dart
        # always executes it, even when the same method is called twice in a row.
        self.__cmd_counter = 0

    # ── Flet internals ────────────────────────────────────────────────────────

    def _get_control_name(self) -> str:
        return "flet_carousel_slider"

    def _get_children(self) -> List[Control]:
        return self.__controls

    # ── Controller methods ────────────────────────────────────────────────────

    def _next_cmd(self) -> int:
        self.__cmd_counter += 1
        return self.__cmd_counter

    def animate_to_page(
        self,
        index: int,
        duration: int = 800,
        curve: AnimateToCurve = AnimateToCurve.FAST_OUT_SLOW_IN,
    ) -> None:
        """Animate to the given page ``index``."""
        curve_id = curve.value if isinstance(curve, AnimateToCurve) else str(curve)
        self._set_attr("__animateTo", f"{index}:{duration}:{curve_id}:{self._next_cmd()}")
        self.update()

    def next_page(
        self,
        duration: int = 300,
        curve: AnimateToCurve = AnimateToCurve.FAST_OUT_SLOW_IN,
    ) -> None:
        """Animate to the next page."""
        curve_id = curve.value if isinstance(curve, AnimateToCurve) else str(curve)
        self._set_attr("__animateTo", f"__next:{duration}:{curve_id}:{self._next_cmd()}")
        self.update()

    def previous_page(
        self,
        duration: int = 300,
        curve: AnimateToCurve = AnimateToCurve.FAST_OUT_SLOW_IN,
    ) -> None:
        """Animate to the previous page."""
        curve_id = curve.value if isinstance(curve, AnimateToCurve) else str(curve)
        self._set_attr("__animateTo", f"__prev:{duration}:{curve_id}:{self._next_cmd()}")
        self.update()

    def jump_to_page(self, index: int) -> None:
        """Instantly jump to a page with no animation."""
        self._set_attr("__animateTo", f"__jump:{index}:none:{self._next_cmd()}")
        self.update()

    # ── controls ──────────────────────────────────────────────────────────────

    @property
    def controls(self) -> List[Control]:
        return self.__controls

    @controls.setter
    def controls(self, value: List[Control]):
        self.__controls = value if value is not None else []

    # ── height ────────────────────────────────────────────────────────────────

    @property
    def height(self) -> Optional[float]:
        return self._get_attr("height", data_type="float")

    @height.setter
    def height(self, value: Optional[float]):
        self._set_attr("height", value)

    # ── aspect_ratio ──────────────────────────────────────────────────────────

    @property
    def aspect_ratio(self) -> float:
        return self._get_attr("aspectRatio", data_type="float", def_value=16/9)

    @aspect_ratio.setter
    def aspect_ratio(self, value: float):
        self._set_attr("aspectRatio", value)

    # ── viewport_fraction ─────────────────────────────────────────────────────

    @property
    def viewport_fraction(self) -> float:
        return self._get_attr("viewportFraction", data_type="float", def_value=0.8)

    @viewport_fraction.setter
    def viewport_fraction(self, value: float):
        self._set_attr("viewportFraction", value)

    # ── initial_page ──────────────────────────────────────────────────────────

    @property
    def initial_page(self) -> int:
        return self._get_attr("initialPage", data_type="int", def_value=0)

    @initial_page.setter
    def initial_page(self, value: int):
        self._set_attr("initialPage", value)

    # ── enable_infinite_scroll ────────────────────────────────────────────────

    @property
    def enable_infinite_scroll(self) -> bool:
        return self._get_attr("enableInfiniteScroll", data_type="bool", def_value=True)

    @enable_infinite_scroll.setter
    def enable_infinite_scroll(self, value: bool):
        self._set_attr("enableInfiniteScroll", value)
        
        

    # ── Disable Gesture ────────────────────────────────────────────────

    @property
    def disablegesture(self) -> bool:
        return self._get_attr("disableGesture", data_type="bool", def_value=False)

    @disablegesture.setter
    def disablegesture(self, value: bool):
        self._set_attr("disableGesture", value)
        
    # ── Enable Indicator ────────────────────────────────────────────────

    @property
    def enable_indicator(self) -> bool:
        return self._get_attr("enableindicator", data_type="bool", def_value=True)

    @enable_indicator.setter
    def enable_indicator(self, value: bool):
        self._set_attr("enableindicator", value)
        
        
        
    # ── Indicator Width ────────────────────────────────────────────────

    @property
    def indicatorwidth(self) -> int:
        return self._get_attr("indicatorwidth", data_type="int", def_value=None)

    @indicatorwidth.setter
    def indicatorwidth(self, value: int):
        self._set_attr("indicatorwidth", value)
        
        
    # ── Indicator Inactive Color ────────────────────────────────────────────────

    @property
    def indicator_inactive_color(self) -> ColorValue:
        return self._get_attr("indicatorInactiveColor", data_type="int", def_value=None)

    @indicator_inactive_color.setter
    def indicator_inactive_color(self, value: ColorValue):
        self._set_attr("indicatorInactiveColor", value)

    # ── Indicator Active Color ────────────────────────────────────────────────

    @property
    def indicator_active_color(self) -> ColorValue:
        return self._get_attr("indicatorActiveColor", data_type="bool", def_value=None)

    @indicator_active_color.setter
    def indicator_active_color(self, value: ColorValue):
        self._set_attr("indicatorActiveColor", value)


    # ── Build On Demand ────────────────────────────────────────────────

    @property
    def build_on_demand(self) -> bool:
        return self._get_attr("build_on_demand", data_type="bool", def_value=False)

    @build_on_demand.setter
    def build_on_demand(self, value: bool):
        self._set_attr("build_on_demand", value)


    # ── animate_to_closest ────────────────────────────────────────────────────

    @property
    def animate_to_closest(self) -> bool:
        return self._get_attr("animateToClosest", data_type="bool", def_value=True)

    @animate_to_closest.setter
    def animate_to_closest(self, value: bool):
        self._set_attr("animateToClosest", value)

    # ── reverse ───────────────────────────────────────────────────────────────

    @property
    def reverse(self) -> bool:
        return self._get_attr("reverse", data_type="bool", def_value=False)

    @reverse.setter
    def reverse(self, value: bool):
        self._set_attr("reverse", value)

    # ── auto_play ─────────────────────────────────────────────────────────────

    @property
    def auto_play(self) -> bool:
        return self._get_attr("autoPlay", data_type="bool", def_value=False)

    @auto_play.setter
    def auto_play(self, value: bool):
        self._set_attr("autoPlay", value)

    # ── auto_play_interval ────────────────────────────────────────────────────

    @property
    def auto_play_interval(self) -> int:
        return self._get_attr("autoPlayInterval", data_type="int", def_value=4000)

    @auto_play_interval.setter
    def auto_play_interval(self, value: int):
        self._set_attr("autoPlayInterval", value)

    # ── auto_play_animation_duration ──────────────────────────────────────────

    @property
    def auto_play_animation_duration(self) -> int:
        return self._get_attr("autoPlayAnimationDuration", data_type="int", def_value=800)

    @auto_play_animation_duration.setter
    def auto_play_animation_duration(self, value: int):
        self._set_attr("autoPlayAnimationDuration", value)

    # ── auto_play_curve ───────────────────────────────────────────────────────

    @property
    def auto_play_curve(self) -> AnimateToCurve:
        return self.__auto_play_curve

    @auto_play_curve.setter
    def auto_play_curve(self, value: AnimateToCurve):
        self.__auto_play_curve = value
        self._set_attr(
            "autoPlayCurve",
            value.value if isinstance(value, AnimateToCurve) else value,
        )

    # ── enlarge_center_page ───────────────────────────────────────────────────

    @property
    def enlarge_center_page(self) -> bool:
        return self._get_attr("enlargeCenterPage", data_type="bool", def_value=False)

    @enlarge_center_page.setter
    def enlarge_center_page(self, value: bool):
        self._set_attr("enlargeCenterPage", value)

    # ── enlarge_strategy ──────────────────────────────────────────────────────

    @property
    def enlarge_strategy(self) -> EnlargeStrategy:
        return self.__enlarge_strategy

    @enlarge_strategy.setter
    def enlarge_strategy(self, value: EnlargeStrategy):
        self.__enlarge_strategy = value
        self._set_attr(
            "enlargeStrategy",
            value.value if isinstance(value, EnlargeStrategy) else value,
        )

    # ── enlarge_factor ────────────────────────────────────────────────────────

    @property
    def enlarge_factor(self) -> float:
        return self._get_attr("enlargeFactor", data_type="float", def_value=0.3)

    @enlarge_factor.setter
    def enlarge_factor(self, value: float):
        self._set_attr("enlargeFactor", value)

    # ── page_snapping ─────────────────────────────────────────────────────────

    @property
    def page_snapping(self) -> bool:
        return self._get_attr("pageSnapping", data_type="bool", def_value=True)

    @page_snapping.setter
    def page_snapping(self, value: bool):
        self._set_attr("pageSnapping", value)

    # ── scroll_direction ──────────────────────────────────────────────────────

    @property
    def scroll_direction(self) -> ScrollDirection:
        return self.__scroll_direction

    @scroll_direction.setter
    def scroll_direction(self, value: ScrollDirection):
        self.__scroll_direction = value
        self._set_attr(
            "scrollDirection",
            value.value if isinstance(value, ScrollDirection) else value,
        )

    # ── pause_auto_play_on_touch ──────────────────────────────────────────────

    @property
    def pause_auto_play_on_touch(self) -> bool:
        return self._get_attr("pauseAutoPlayOnTouch", data_type="bool", def_value=True)

    @pause_auto_play_on_touch.setter
    def pause_auto_play_on_touch(self, value: bool):
        self._set_attr("pauseAutoPlayOnTouch", value)

    # ── pause_auto_play_on_manual_navigate ────────────────────────────────────

    @property
    def pause_auto_play_on_manual_navigate(self) -> bool:
        return self._get_attr("pauseAutoPlayOnManualNavigate", data_type="bool", def_value=True)

    @pause_auto_play_on_manual_navigate.setter
    def pause_auto_play_on_manual_navigate(self, value: bool):
        self._set_attr("pauseAutoPlayOnManualNavigate", value)

    # ── pause_auto_play_in_finite_scroll ──────────────────────────────────────

    @property
    def pause_auto_play_in_finite_scroll(self) -> bool:
        return self._get_attr("pauseAutoPlayInFiniteScroll", data_type="bool", def_value=False)

    @pause_auto_play_in_finite_scroll.setter
    def pause_auto_play_in_finite_scroll(self, value: bool):
        self._set_attr("pauseAutoPlayInFiniteScroll", value)

    # ── disable_center ────────────────────────────────────────────────────────

    @property
    def disable_center(self) -> bool:
        return self._get_attr("disableCenter", data_type="bool", def_value=False)

    @disable_center.setter
    def disable_center(self, value: bool):
        self._set_attr("disableCenter", value)

    # ── pad_ends ──────────────────────────────────────────────────────────────

    @property
    def pad_ends(self) -> bool:
        return self._get_attr("padEnds", data_type="bool", def_value=True)

    @pad_ends.setter
    def pad_ends(self, value: bool):
        self._set_attr("padEnds", value)

    # ── clip_behavior ─────────────────────────────────────────────────────────

    @property
    def clip_behavior(self) -> ClipBehavior:
        return self.__clip_behavior

    @clip_behavior.setter
    def clip_behavior(self, value: ClipBehavior):
        self.__clip_behavior = value
        self._set_attr(
            "clipBehavior",
            value.value if isinstance(value, ClipBehavior) else value,
        )

    # ── on_change ─────────────────────────────────────────────────────────────

    @property
    def on_change(self) -> Optional[Callable[[CarouselChangeEvent], None]]:
        return self.__on_change

    @on_change.setter
    def on_change(self, handler: Optional[Callable[[CarouselChangeEvent], None]]):
        self.__on_change = handler
        def _wrap(e: ControlEvent):
            if handler:
                handler(CarouselChangeEvent(e))
        self._add_event_handler("change", _wrap if handler else None)

    # ── on_scrolled ───────────────────────────────────────────────────────────

    @property
    def on_scrolled(self) -> Optional[Callable[[CarouselScrolledEvent], None]]:
        return self.__on_scrolled

    @on_scrolled.setter
    def on_scrolled(self, handler: Optional[Callable[[CarouselScrolledEvent], None]]):
        self.__on_scrolled = handler
        def _wrap(e: ControlEvent):
            if handler:
                handler(CarouselScrolledEvent(e))
        self._add_event_handler("scrolled", _wrap if handler else None)