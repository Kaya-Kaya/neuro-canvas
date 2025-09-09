import random
import string
import pytest

from typing import Final

from .canvas import Canvas, Coordinate
from .constants import SCREEN_WIDTH, SCREEN_HEIGHT, BEZIER_STEPS


REPEAT_AMOUNT: Final[int] = 1000


def setup_canvas() -> Canvas:
    if hasattr(Canvas, "instance"):
        del Canvas.instance
    return Canvas()


def random_coordinate() -> Coordinate:
    return random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)


def random_string() -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(4, REPEAT_AMOUNT)))


def test_draw_line():
    canvas = setup_canvas()

    for _ in range(REPEAT_AMOUNT):
        canvas.draw_line(random_coordinate(), random_coordinate())


def test_draw_lines():
    canvas = setup_canvas()

    for _ in range(REPEAT_AMOUNT):
        canvas.draw_lines([random_coordinate() for _ in range(random.randint(3, 10))],
                          random.choice((True, False)))


def test_draw_curve():
    canvas = setup_canvas()

    for _ in range(REPEAT_AMOUNT):
        canvas.draw_curve([random_coordinate() for _ in range(random.randint(3, 10))], BEZIER_STEPS)


def test_draw_circle():
    canvas = setup_canvas()

    for _ in range(REPEAT_AMOUNT):
        canvas.draw_circle(random_coordinate(), random.randint(1, max(SCREEN_HEIGHT, SCREEN_WIDTH)))


def test_draw_rectangle():
    canvas = setup_canvas()

    for _ in range(REPEAT_AMOUNT):
        canvas.draw_rectangle(random_coordinate(), random_coordinate())


def test_draw_triangle():
    canvas = setup_canvas()

    for _ in range(REPEAT_AMOUNT):
        canvas.draw_triangle(
            random_coordinate(),
            random.randint(1, max(SCREEN_HEIGHT, SCREEN_WIDTH)),
            random.uniform(0, 120)
        )


def test_layers():
    canvas = setup_canvas()

    added_layers = {"background", "base"}

    # Add layers
    for _ in range(REPEAT_AMOUNT):
        layer_name = random_string()
        assert canvas.layer_exists(layer_name) == (layer_name in added_layers)

        canvas.add_layer(layer_name)
        added_layers.add(layer_name)
        assert canvas.layer_exists(layer_name)

    # Switch active layer
    for layer in added_layers:
        if layer == "background":
            continue

        canvas.switch_active_layer(layer)
        assert layer == canvas.get_active_layer()

    # Try to switch to non-existent layer
    for _ in range(REPEAT_AMOUNT):
        layer_name = random_string()

        if layer_name in added_layers:
            continue

        canvas.switch_active_layer(layer_name)

        assert layer_name != canvas.get_active_layer()

    # Remove layers
    for layer in added_layers:
        if layer in ("background", "base"):
            continue

        assert canvas.layer_exists(layer)

        canvas.remove_layer(layer)
        assert not canvas.layer_exists(layer)


def test_layer_visibility():
    canvas = setup_canvas()

    for _ in range(REPEAT_AMOUNT):
        layer_name = random_string()

        if layer_name in ("background", "base"):
            continue

        with pytest.raises(ValueError):
            canvas.set_layer_visibility(layer_name, random.random())


def test_bucket_fill():
    canvas = setup_canvas()

    for _ in range(REPEAT_AMOUNT):
        coords = random_coordinate()

        if (coords[0] == SCREEN_WIDTH) or (coords[1] == SCREEN_HEIGHT):
            continue

        canvas.bucket_fill(coords)


def test_undo():
    canvas = setup_canvas()

    assert not canvas.undo()

    for _ in range(REPEAT_AMOUNT):
        canvas.draw_line(random_coordinate(), random_coordinate())

    for _ in range(REPEAT_AMOUNT):
        assert canvas.undo()

    assert not canvas.undo()


def test_export(tmp_path):
    canvas = setup_canvas()

    for _ in range(REPEAT_AMOUNT):
        filename = random_string()[:20]
        filetype = random.choice(["bmp", "tga", "png", "jpg"])

        canvas.export(filename, filetype, tmp_path)
        assert (tmp_path / f"{filename}.{filetype}").exists()  # type: ignore
