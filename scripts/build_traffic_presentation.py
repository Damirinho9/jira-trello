#!/usr/bin/env python3
"""Builds the PowerPoint assignment slide (car + traffic light) via Python.

This script targets Windows + Microsoft PowerPoint using COM automation.
It creates one slide with:
- arc road
- car shape (emoji fallback)
- traffic light
- animation timeline approximating table 3.1 from the provided methodical guide

Run (on Windows with PowerPoint installed):
    python scripts/build_traffic_presentation.py --output task4_traffic.pptx
"""

from __future__ import annotations

import argparse
import pathlib

import win32com.client  # type: ignore
from pywintypes import com_error  # type: ignore


# RGB helper (PowerPoint expects BGR integer)
def rgb(r: int, g: int, b: int) -> int:
    return r + (g << 8) + (b << 16)


# Office / PowerPoint constants (numeric, to avoid makepy dependency)
MSO_TRUE = -1
MSO_FALSE = 0

PP_LAYOUT_BLANK = 12

MSO_SHAPE_RECTANGLE = 1
MSO_SHAPE_OVAL = 9
MSO_SHAPE_ARC = 25

# Triggers
MSO_ANIM_TRIGGER_WITH_PREVIOUS = 2
MSO_ANIM_TRIGGER_AFTER_PREVIOUS = 3

# Effects
MSO_ANIM_EFFECT_CUSTOM = 0
MSO_ANIM_EFFECT_SPIN = 61
MSO_ANIM_EFFECT_CHANGE_FILL_COLOR = 54

# Behavior types
MSO_ANIM_TYPE_MOTION = 1
MSO_ANIM_TYPE_COLOR = 3


class PresentationBuilder:
    def __init__(self, output_path: pathlib.Path) -> None:
        self.output_path = output_path
        self.app = None
        self.presentation = None
        self.slide = None

    def build(self) -> None:
        self.app = win32com.client.Dispatch("PowerPoint.Application")
        self.app.Visible = MSO_TRUE

        self.presentation = self.app.Presentations.Add()
        self.slide = self.presentation.Slides.Add(1, PP_LAYOUT_BLANK)

        slide_w = self.presentation.PageSetup.SlideWidth
        slide_h = self.presentation.PageSetup.SlideHeight

        scene = self._draw_scene(slide_w, slide_h)
        self._configure_animation(scene)

        self.presentation.SaveAs(str(self.output_path.resolve()))
        self.presentation.Close()
        self.app.Quit()

    def _draw_scene(self, slide_w: float, slide_h: float) -> dict[str, object]:
        # Road (arc)
        road = self.slide.Shapes.AddShape(
            MSO_SHAPE_ARC,
            slide_w * 0.04,
            slide_h * 0.18,
            slide_w * 0.90,
            slide_h * 0.80,
        )
        road.Fill.Visible = MSO_FALSE
        road.Line.Visible = MSO_TRUE
        road.Line.ForeColor.RGB = rgb(90, 90, 90)
        road.Line.Weight = 70

        # Car body (simple rounded rectangle + wheels)
        car_group = self._draw_car(slide_w, slide_h)

        # Traffic light (pole + lights)
        traffic = self._draw_traffic_light(slide_w, slide_h)

        return {
            "road": road,
            "car": car_group,
            "red": traffic["red"],
            "yellow": traffic["yellow"],
            "green": traffic["green"],
        }

    def _draw_car(self, slide_w: float, slide_h: float):
        body = self.slide.Shapes.AddShape(
            MSO_SHAPE_RECTANGLE,
            slide_w * 0.11,
            slide_h * 0.24,
            120,
            44,
        )
        body.Fill.ForeColor.RGB = rgb(35, 35, 35)
        body.Line.Visible = MSO_FALSE

        roof = self.slide.Shapes.AddShape(
            MSO_SHAPE_RECTANGLE,
            slide_w * 0.145,
            slide_h * 0.205,
            70,
            24,
        )
        roof.Fill.ForeColor.RGB = rgb(45, 45, 45)
        roof.Line.Visible = MSO_FALSE

        wheel1 = self.slide.Shapes.AddShape(MSO_SHAPE_OVAL, slide_w * 0.125, slide_h * 0.29, 24, 24)
        wheel2 = self.slide.Shapes.AddShape(MSO_SHAPE_OVAL, slide_w * 0.215, slide_h * 0.29, 24, 24)
        for wheel in (wheel1, wheel2):
            wheel.Fill.ForeColor.RGB = rgb(10, 10, 10)
            wheel.Line.Visible = MSO_FALSE

        group_range = self.slide.Shapes.Range([body.Name, roof.Name, wheel1.Name, wheel2.Name])
        car = group_range.Group()
        car.Rotation = 8
        return car

    def _draw_traffic_light(self, slide_w: float, slide_h: float) -> dict[str, object]:
        pole = self.slide.Shapes.AddShape(
            MSO_SHAPE_RECTANGLE,
            slide_w * 0.74,
            slide_h * 0.28,
            12,
            210,
        )
        pole.Fill.ForeColor.RGB = rgb(30, 30, 30)
        pole.Line.Visible = MSO_FALSE

        housing = self.slide.Shapes.AddShape(
            MSO_SHAPE_RECTANGLE,
            slide_w * 0.705,
            slide_h * 0.24,
            82,
            170,
        )
        housing.Fill.ForeColor.RGB = rgb(55, 55, 55)
        housing.Line.Visible = MSO_FALSE

        red = self.slide.Shapes.AddShape(MSO_SHAPE_OVAL, slide_w * 0.725, slide_h * 0.255, 42, 42)
        yellow = self.slide.Shapes.AddShape(MSO_SHAPE_OVAL, slide_w * 0.725, slide_h * 0.315, 42, 42)
        green = self.slide.Shapes.AddShape(MSO_SHAPE_OVAL, slide_w * 0.725, slide_h * 0.375, 42, 42)

        base = rgb(85, 85, 85)
        for lamp in (red, yellow, green):
            lamp.Fill.ForeColor.RGB = base
            lamp.Line.Visible = MSO_FALSE

        return {"pole": pole, "housing": housing, "red": red, "yellow": yellow, "green": green}

    def _add_motion_path(self, shape, trigger: int, duration: float, delay: float, path: str):
        seq = self.slide.TimeLine.MainSequence
        effect = seq.AddEffect(shape, MSO_ANIM_EFFECT_CUSTOM, trigger=trigger)
        behavior = effect.Behaviors.Add(MSO_ANIM_TYPE_MOTION)
        behavior.MotionEffect.Path = path
        effect.Timing.Duration = duration
        effect.Timing.TriggerDelayTime = delay
        return effect

    def _add_spin(self, shape, trigger: int, degrees: float, duration: float, delay: float):
        seq = self.slide.TimeLine.MainSequence
        effect = seq.AddEffect(shape, MSO_ANIM_EFFECT_SPIN, trigger=trigger)
        effect.EffectParameters.Amount = degrees
        effect.Timing.Duration = duration
        effect.Timing.TriggerDelayTime = delay
        return effect

    def _add_color_emphasis(self, shape, trigger: int, color: int, duration: float, delay: float):
        seq = self.slide.TimeLine.MainSequence

        # Preferred path: add a custom effect with color behavior.
        # Some PowerPoint builds raise `Invalid request` for ColorEffect on custom behavior,
        # so we gracefully fallback to the built-in ChangeFillColor emphasis effect.
        try:
            effect = seq.AddEffect(shape, MSO_ANIM_EFFECT_CUSTOM, trigger=trigger)
            behavior = effect.Behaviors.Add(MSO_ANIM_TYPE_COLOR)
            behavior.ColorEffect.To.RGB = color
        except com_error:
            effect = seq.AddEffect(shape, MSO_ANIM_EFFECT_CHANGE_FILL_COLOR, trigger=trigger)
            # Different Office versions expose target color on different properties.
            # We try known options and then continue even if not writable.
            for attr in ("Color2", "Color1", "Color"):
                try:
                    getattr(effect.EffectParameters, attr).RGB = color
                    break
                except Exception:
                    continue

        effect.Timing.Duration = duration
        effect.Timing.TriggerDelayTime = delay
        return effect

    def _configure_animation(self, scene: dict[str, object]) -> None:
        car = scene["car"]
        red = scene["red"]
        yellow = scene["yellow"]
        green = scene["green"]

        # 1) Car first motion path (approach traffic light)
        self._add_motion_path(
            car,
            trigger=MSO_ANIM_TRIGGER_AFTER_PREVIOUS,
            duration=2.0,
            delay=0.0,
            path="M 0 0 C 0.15 0.07 0.34 0.20 0.53 0.30",
        )

        # 2) Car rotation 17° (clockwise)
        self._add_spin(
            car,
            trigger=MSO_ANIM_TRIGGER_WITH_PREVIOUS,
            degrees=17,
            duration=1.5,
            delay=0.1,
        )

        # 3) Red ON
        self._add_color_emphasis(
            red,
            trigger=MSO_ANIM_TRIGGER_WITH_PREVIOUS,
            color=rgb(220, 35, 35),
            duration=0.4,
            delay=1.0,
        )

        # 4) Red OFF
        self._add_color_emphasis(
            red,
            trigger=MSO_ANIM_TRIGGER_AFTER_PREVIOUS,
            color=rgb(85, 85, 85),
            duration=0.4,
            delay=0.0,
        )

        # 5) Yellow ON
        self._add_color_emphasis(
            yellow,
            trigger=MSO_ANIM_TRIGGER_WITH_PREVIOUS,
            color=rgb(230, 190, 40),
            duration=0.4,
            delay=0.0,
        )

        # 6) Yellow OFF
        self._add_color_emphasis(
            yellow,
            trigger=MSO_ANIM_TRIGGER_AFTER_PREVIOUS,
            color=rgb(85, 85, 85),
            duration=0.4,
            delay=0.0,
        )

        # 7) Green ON
        self._add_color_emphasis(
            green,
            trigger=MSO_ANIM_TRIGGER_WITH_PREVIOUS,
            color=rgb(40, 180, 75),
            duration=0.4,
            delay=1.0,
        )

        # 8) Car second motion path (continue after green)
        self._add_motion_path(
            car,
            trigger=MSO_ANIM_TRIGGER_WITH_PREVIOUS,
            duration=1.2,
            delay=0.5,
            path="M 0 0 C 0.12 0.06 0.27 0.13 0.42 0.18",
        )

        # 9) Car final rotation 25°
        self._add_spin(
            car,
            trigger=MSO_ANIM_TRIGGER_WITH_PREVIOUS,
            degrees=25,
            duration=1.5,
            delay=0.1,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build task #4 traffic animation PPTX")
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("task4_traffic.pptx"),
        help="Output pptx file path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    builder = PresentationBuilder(args.output)
    builder.build()
    print(f"Presentation saved to: {args.output}")


if __name__ == "__main__":
    main()
