import argparse as ap
from numbers import Real
from typing import Self
from typing import Optional

import pygame as pg
from pygame.typing import ColorLike

from trace import Object
from trace import Floor
from trace import Sphere
from trace import Light
from trace import Camera
from trace import Scene


class Game(object):

    _DEFAULT_SIZE = (640, 480)
    _DEFAULT_FILENAME = 'render.png'

    def __init__(self: Self) -> None:
        pg.init()

        self._scene = Scene(
            objects={
                Floor(0, 2, (255, 255, 255), (0, 0, 0), 0.35),
                Sphere((-3, 1, 12), 1, (255, 0, 0), 0.25),
                Sphere((0, 1, 12), 1, (0, 255, 0), 0.25),
                Sphere((3, 1, 12), 1, (0, 0, 255), 0.25),
                Sphere((-3, 3, 12), 1, (0, 255, 255), 0.25),
                Sphere((0, 3, 12), 1, (255, 0, 255), 0.25),
                Sphere((3, 3, 12), 1, (255, 255, 0), 0.25),
                Sphere((-3, 5, 12), 1, (0, 0, 0), 0.25),
                Sphere((0, 5, 12), 1, (128, 128, 128), 0.25),
                Sphere((3, 5, 12), 1, (255, 255, 255), 0.25),
            },
            lights={
                Light(pg.Vector3(0, 3, 0), color=(255, 255, 255)),
                Light(pg.Vector3(0, 12, 12), color=(255, 255, 255)),
            },
            camera=Camera(
                pos=pg.Vector3(0, 3, 0),
                rot=pg.Vector3(0, 0, 0),
                max_reflect=8,
            ),
        )

        self._parser = ap.ArgumentParser(
            prog='shittypythonraytracer',
            description='a shitty raytracer program',
            epilog='cureated by Tomatofu',
        )
        self._parser.add_argument(
            '-s', '--size',
            nargs=2,
            default=self._DEFAULT_SIZE,
            type=int,
            help='size (w, h) in (px) of render',
        )
        self._parser.add_argument(
            '-p', '--path',
            default=self._DEFAULT_FILENAME,
            type=str,
            help='filepath to render to',
        )

    def run(self: Self) -> None:
        args = self._parser.parse_args()
        surf = pg.Surface(args.size)
        self._scene.render(surf)
        pg.image.save(surf, args.path)
        pg.quit()


if __name__ == '__main__':
    Game().run()

