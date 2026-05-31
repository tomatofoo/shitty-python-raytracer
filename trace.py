from __future__ import annotations

import math
import random
from numbers import Real
from typing import Self
from typing import Optional

import pygame as pg
from pygame.typing import ColorLike


class Reflection(object):
    def __init__(self: Self,
                 obj: Object,
                 color: ColorLike,
                 mult: Real | pg.Vector3,
                 pos: Optional[pg.Vector3],
                 vector: Optional[pg.Vector3]=None) -> None:
        self._obj = obj
        self._color = color
        self.mult = pg.Vector3(mult)
        self._pos = pos
        self.vector = vector

    @property
    def obj(self: Self) -> Object:
        return self._obj

    @obj.setter
    def obj(self: Self, value: Object) -> None:
        self._obj = value

    @property
    def color(self: Self) -> ColorLike:
        return self._color

    @color.setter
    def color(self: Self, value: ColorLike) -> None:
        self._color = color

    @property
    def mult(self: Self) -> pg.Vector3:
        return self._mult

    @mult.setter
    def mult(self: Self, value: Real | pg.Vector3) -> None:
        value = pg.Vector3(value)
        value.update(max(value[0], 0), max(value[1], 0), max(value[2], 0))
        self._mult = value
        div = max(value)
        if div > 1:
            self._mult = value / div

    @property
    def pos(self: Self) -> Optional[pg.Vector3]:
        return self._pos

    @pos.setter
    def pos(self: Self, value: Optional[pg.Vector3]) -> None:
        self._pos = value

    @property
    def vector(self: Self) -> Optional[pg.Vector3]:
        return self._vector

    @vector.setter
    def vector(self: Self, value: Optional[pg.Vector3]) -> None:
        if value: # prevents None and zero vector
            self._vector = value
        else:
            self._vector = None


class Object(object):
    
    _BLANK = Reflection(None, (0, 0, 0), 0, None, None)

    def __init__(self: Self,
                 pos: pg.Vector3,
                 color: ColorLike,
                 reflection: Real | pg.Vector3,
                 reflection_diffuse: Real=1,
                 diffuse: Real=0,
                 specular: Real=1,
                 exponent: Real=32) -> None:
        self._scene = None
        self._pos = pos
        self._color = color
        self.reflection = reflection
        self._reflection_diffuse = reflection_diffuse
        self._diffuse = diffuse
        self._specular = specular
        self._exponent = exponent

    @property
    def pos(self: Self) -> pg.Vector3:
        return self._pos

    @pos.setter
    def pos(self: Self, value: pg.Vector3) -> None:
        self._pos = value

    @property
    def color(self: Self) -> ColorLike:
        return self._color

    @color.setter
    def color(self: Self, value: ColorLike) -> None:
        self._color = value

    @property
    def reflection(self: Self) -> pg.Vector3:
        return self._reflection

    @reflection.setter
    def reflection(self: Self, value: Real | pg.Vector3) -> None:
        value = pg.Vector3(value)
        value.update(max(value[0], 0), max(value[1], 0), max(value[2], 0))
        self._reflection = value
        div = max(value)
        if div > 1:
            self._reflection = value / div

    @property
    def reflection_diffuse(self: Self) -> Real:
        return self._reflection_diffuse

    @reflection_diffuse.setter
    def reflection_diffuse(self: Self, value: Real) -> None:
        self._reflection_diffuse = value

    @property
    def diffuse(self: Self) -> Real:
        return self._diffuse

    @diffuse.setter
    def diffuse(self: Self, value: Real) -> None:
        self._diffuse = value

    @property
    def specular(self: Self) -> Real:
        return self._specular

    @specular.setter
    def specular(self: Self, value: Real) -> None:
        self._specular = value

    @property
    def exponent(self: Self) -> Real:
        return self._exponent

    @exponent.setter
    def exponent(self: Self, value: Real) -> None:
        self._exponent = value

    def _new_color(self: Self,
                   pos: pg.Vector3,
                   normal: pg.Vector3, # assumed to be normalized
                   new_vector: pg.Vector3,
                   color: ColorLike,
                   reflection: Reflection) -> ColorLike:
        mult = 0
        diffuse = [0, 0, 0]
        specular = [0, 0, 0]
        for light in self._scene._lights:
            rel = (pos - light._pos).normalize()
            for obj in self._scene._objects:
                if obj is self:
                    continue
                intersection = obj.intersects(
                    Reflection(None, (0, 0, 0), 0, pos, -rel),
                )
                if intersection is None:
                    continue
                # check if is in front by checking if same sign
                intersection_rel = intersection - light._pos
                if ((intersection_rel[0] < 0) == (rel[0] < 0)
                    and (intersection_rel[1] < 0) == (rel[1] < 0)
                    and (intersection_rel[2] < 0) == (rel[2] < 0)):
                    break
            else:
                d = max(-rel.dot(normal), 0)
                s = max(-rel.dot(new_vector.normalize()), 0)**self._exponent
                mult += d
                diffuse[0] += d * light._color[0] / 255
                diffuse[1] += d * light._color[1] / 255
                diffuse[2] += d * light._color[2] / 255
                specular[0] += s * light._color[0] / 255
                specular[1] += s * light._color[1] / 255
                specular[2] += s * light._color[2] / 255
        color = (
            int(pg.math.clamp(
                reflection._color[0]
                + reflection._mult[0] * (
                    diffuse[0] * color[0] * self._reflection_diffuse
                    + diffuse[0] * 255 * self._diffuse
                    + specular[0] * 255 * self._specular
                    - reflection._color[0]
                ),
                0, 255,
            )),
            int(pg.math.clamp(
                reflection._color[1]
                + reflection._mult[1] * (
                    diffuse[1] * color[1] * self._reflection_diffuse
                    + diffuse[1] * 255 * self._diffuse
                    + specular[1] * 255 * self._specular
                    - reflection._color[1]
                ),
                0, 255,
            )),
            int(pg.math.clamp(
                reflection._color[2]
                + reflection._mult[2] * (
                    diffuse[2] * color[2] * self._reflection_diffuse
                    + diffuse[2] * 255 * self._diffuse
                    + specular[2] * 255 * self._specular
                    - reflection._color[2]
                ),
                0, 255,
            )),
        )
        return color, mult

    def _new_mult(self: Self, reflection: Reflection, mult: Real) -> pg.Vector3:
        return pg.Vector3(
            self._reflection[0] * reflection._mult[0],
            self._reflection[1] * reflection._mult[1],
            self._reflection[2] * reflection._mult[2],
        ) * mult

    def intersects(self: Self, reflection: Reflection) -> Optional[pg.Vector3]:
        return pg.Vector3(0, 0, 0)

    def reflect(self: Self, reflection: Reflection) -> Reflection:
        return reflection


class Floor(Object):
    def __init__(self: Self,
                 y: Real,
                 period: Real,
                 color1: ColorLike,
                 color2: ColorLike,
                 reflection: Real | pg.Vector3,
                 reflection_diffuse: Real=1,
                 diffuse: Real=0,
                 specular: Real=1,
                 exponent: Real=32) -> None:
        super().__init__(
            pg.Vector3(0, y, 0),
            (0, 0, 0),
            reflection,
            reflection_diffuse,
            diffuse,
            specular,
            exponent,
        )
        self._y = y
        self.period = period
        self._color1 = color1
        self._color2 = color2

    @property
    def color1(self: Self) -> ColorLike:
        return self._color1

    @color1.setter
    def color1(self: Self, value: ColorLike) -> None:
        self._color1 = value

    @property
    def color2(self: Self) -> ColorLike:
        return self._color2

    @color2.setter
    def color2(self: Self, value: ColorLike) -> None:
        self._color2 = value

    @property
    def period(self: Self) -> Real:
        return self._period

    @period.setter
    def period(self: Self, value: Real) -> None:
        self._period = value
        self._semiperiod = value / 2

    @property
    def y(self: Self) -> Real:
        return self._y

    @y.setter
    def y(self: Self, value: Real) -> None:
        self._y = value

    def intersects(self: Self, reflection: Reflection) -> Optional[pg.Vector3]:
        if reflection._vector[1] >= 0:
            return None
        diff = self._y - reflection._pos[1]
        return pg.Vector3(
            reflection._pos[0]
            + reflection._vector[0] / reflection._vector[1] * diff,
            self._y,
            reflection._pos[2]
            + reflection._vector[2] / reflection._vector[1] * diff,
        )

    def reflect(self: Self, reflection: Reflection) -> Reflection:
        if reflection._vector[1] >= 0:
            return self._BLANK

        diff = self._y - reflection._pos[1]
        pos = pg.Vector3(
            reflection._pos[0]
            + reflection._vector[0] / reflection._vector[1] * diff,
            self._y,
            reflection._pos[2]
            + reflection._vector[2] / reflection._vector[1] * diff,
        )
        if ((pos[0] % self._period < self._semiperiod)
            == (pos[2] % self._period < self._semiperiod)):
            color = self._color1
        else:
            color = self._color2
        normal = (0, 1, 0)
        new_vector = reflection._vector.reflect(normal)
        color, mult = self._new_color(
            pos, normal, new_vector, color, reflection,
        )
        return Reflection(
            self,
            color,
            self._new_mult(reflection, mult),
            pos,
            new_vector,
        )


class Sphere(Object):
    def __init__(self: Self,
                 pos: pg.Vector3,
                 radius: Real,
                 color: ColorLike,
                 reflection: Real | pg.Vector3,
                 reflection_diffuse: Real=1,
                 diffuse: Real=0,
                 specular: Real=1,
                 exponent: Real=32) -> None:
        super().__init__(
            pos,
            color,
            reflection,
            reflection_diffuse,
            diffuse,
            specular,
            exponent,
        )
        self._radius = radius

    @property
    def radius(self: Self) -> Real:
        return self._radius

    @radius.setter
    def radius(self: Self, value: Real) -> None:
        self._radius = value

    def intersects(self: Self, reflection: Reflection) -> Optional[pg.Vector3]:
        end = reflection._pos + reflection._vector
        r_squared = self._radius * self._radius
        a = (
            (reflection._pos[0] - end[0])**2
            + (reflection._pos[1] - end[1])**2
            + (reflection._pos[2] - end[2])**2
        )
        c = (
            (reflection._pos[0] - self._pos[0])**2
            + (reflection._pos[1] - self._pos[1])**2
            + (reflection._pos[2] - self._pos[2])**2
            - r_squared
        )
        b = (
            (end[0] - self._pos[0])**2
            + (end[1] - self._pos[1])**2
            + (end[2] - self._pos[2])**2
            - a - c - r_squared
        )
        disc = b * b - 4 * a * c # discriminant
        if disc < 0:
            return None
        t1 = (-b + math.sqrt(disc)) / (2 * a)
        point1 = reflection._pos + reflection._vector * t1
        if disc == 0:
            if t1 < 0:
                return None
            return point1
        t2 = (-b - math.sqrt(disc)) / (2 * a)
        point2 = reflection._pos + reflection._vector * t2
        if (reflection._pos.distance_to(point1)
            < reflection._pos.distance_to(point2)):
            if t1 < 0:
                return None
            return point2
        if t2 < 0:
            return None
        return point2

    def reflect(self: Self, reflection: Reflection) -> Reflection:
        # https://stackoverflow.com/a/5883559
        end = reflection._pos + reflection._vector
        r_squared = self._radius * self._radius
        a = (
            (reflection._pos[0] - end[0])**2
            + (reflection._pos[1] - end[1])**2
            + (reflection._pos[2] - end[2])**2
        )
        c = (
            (reflection._pos[0] - self._pos[0])**2
            + (reflection._pos[1] - self._pos[1])**2
            + (reflection._pos[2] - self._pos[2])**2
            - r_squared
        )
        b = (
            (end[0] - self._pos[0])**2
            + (end[1] - self._pos[1])**2
            + (end[2] - self._pos[2])**2
            - a - c - r_squared
        )
        disc = b * b - 4 * a * c # discriminant
        if disc < 0:
            return self._BLANK
        # color = self._new_color(self._color, reflection)
        t1 = (-b + math.sqrt(disc)) / (2 * a)
        point1 = reflection._pos + reflection._vector * t1
        if disc == 0:
            if t1 < 0:
                return self._BLANK
            normal = (point1 - self._pos).normalize()
            new_vector = reflection._vector.reflect(normal)
            color, mult = self._new_color(
                point1, normal, new_vector, self._color, reflection,
            )
            return Reflection(
                self,
                color,
                self._new_mult(reflection, mult),
                point1,
                new_vector,
            )
        t2 = (-b - math.sqrt(disc)) / (2 * a)
        point2 = reflection._pos + reflection._vector * t2
        if (reflection._pos.distance_to(point1)
            < reflection._pos.distance_to(point2)):
            if t1 < 0:
                return self._BLANK
            normal = (point1 - self._pos).normalize()
            new_vector = reflection._vector.reflect(normal)
            color, mult = self._new_color(
                point1, normal, new_vector, self._color, reflection,
            )
            return Reflection(
                self,
                color,
                self._new_mult(reflection, mult),
                point1,
                new_vector,
            )
        if t2 < 0:
            return self._BLANK
        normal = (point2 - self._pos).normalize()
        new_vector = reflection._vector.reflect(normal)
        color, mult = self._new_color(
            point2, normal, new_vector, self._color, reflection,
        )
        return Reflection(
            self,
            color,
            self._new_mult(reflection, mult),
            point2,
            new_vector, 
        )


class Light(object):
    def __init__(self: Self,
                 pos: pg.Vector3,
                 color: ColorLike=(255, 255, 255)) -> None:
        self._pos = pos
        self._color = color

    @property
    def pos(self: Self) -> pg.Vector3:
        return self._pos

    @pos.setter
    def pos(self: Self, value: pg.Vector3) -> None:
        self._pos = value

    @property
    def color(self: Self) -> ColorLike:
        return self._color

    @color.setter
    def color(self: Self, value: ColorLike) -> None:
        self._color = value


class Camera(object):
    def __init__(self: Self,
                 pos: pg.Vector3,
                 rot: pg.Vector3,
                 fov: Real=90,
                 color: ColorLike=(255, 255, 255),
                 max_reflect: int=5) -> None:
        self.fov = fov
        self._color = color
        self._max_reflect = max_reflect
        self._pos = pos
        self.rot = rot

    @property
    def pos(self: Self) -> pg.Vector3:
        return self._pos

    @pos.setter
    def pos(self: Self, value: pg.Vector3) -> None:
        self._pos = value

    @property
    def x(self: Self) -> Real:
        return self._pos[0]

    @x.setter
    def x(self: Self, value: Real) -> None:
        self._pos[0] = value

    @property
    def y(self: Self) -> Real:
        return self._pos[1]

    @y.setter
    def y(self: Self, value: Real) -> None:
        self._pos[1] = value

    @property
    def z(self: Self) -> Real:
        return self._pos[2]

    @z.setter
    def z(self: Self, value: Real) -> None:
        self._pos[2] = value

    @property
    def rot(self: Self) -> pg.Vector3:
        return self._rot

    @rot.setter
    def rot(self: Self, value: pg.Vector3) -> None:
        self._rot = value
        self._semiwidth = pg.Vector3(1, 0, 0)
        self._semiheight = pg.Vector3(0, -1, 0) # y is flipped
        self._focal_vector = pg.Vector3(0, 0, self._focal_length)
        self._semiwidth.rotate_y_ip(self._rot[1])
        self._semiwidth.rotate_x_ip(self._rot[0])
        self._semiwidth.rotate_z_ip(self._rot[2])
        self._semiheight.rotate_y_ip(self._rot[1])
        self._semiheight.rotate_x_ip(self._rot[0])
        self._semiheight.rotate_z_ip(self._rot[2])
        self._focal_vector.rotate_y_ip(self._rot[1]) 
        self._focal_vector.rotate_x_ip(self._rot[0]) 
        self._focal_vector.rotate_z_ip(self._rot[2]) 

    @property
    def pitch(self: Self) -> Real:
        return self._rot[0]

    @pitch.setter
    def pitch(self: Self, value: Real) -> None:
        self._rot[0] = value

    @property
    def yaw(self: Self) -> Real:
        return self._rot[1]

    @yaw.setter
    def yaw(self: Self, value: Real) -> None:
        self._rot[1] = value

    @property
    def roll(self: Self) -> Real:
        return self._rot[2]

    @roll.setter
    def roll(self: Self, value: Real) -> None:
        self._rot[2] = value

    @property
    def fov(self: Self) -> Real:
        return self._fov

    @fov.setter
    def fov(self: Self, value: Real) -> None:
        self._fov = value
        self._focal_length = 1 / math.tan(math.radians(value / 2))

    @property
    def color(self: Self) -> ColorLike:
        return self._color

    @color.setter
    def color(self: Self, value: ColorLike) -> None:
        self._color = value

    @property
    def max_reflect(self: Self) -> int:
        return self._max_reflect

    @max_reflect.setter
    def max_reflect(self: Self, value: int) -> None:
        self._max_reflect = value


class Scene(object):
    def __init__(self: Self,
                 objects: set[Object],
                 lights: set[Light],
                 camera: Camera) -> None:
        self._objects = objects
        for obj in self._objects:
            obj._scene = self
        self._lights = lights
        self._camera = camera

    @property
    def objects(self: Self) -> set[Object]:
        return self._objects

    @objects.setter
    def objects(self: Self, value: set[Object]) -> None:
        for obj in self._objects:
            obj._scene = None
        self._objects = value
        for obj in self._objects:
            obj._scene = self

    @property
    def lights(self: Self) -> set[Light]:
        return self._lights

    @lights.setter
    def lights(self: Self, value: set[Light]) -> None:
        self._lights = value

    @property
    def camera(self: Self) -> Camera:
        return self._camera

    @camera.setter
    def camera(self: Self, value: Camera) -> None:
        self._camera = value

    def render(self: Self, surf: pg.Surface) -> None:
        for y in range(surf.height):
            for x in range(surf.width):
                reflection = Reflection(
                    None,
                    (0, 0, 0),
                    1,
                    self._camera.pos,
                    (x - surf.width / 2)
                    / surf.width
                    * self._camera._semiwidth
                    + (y - surf.height / 2)
                    / surf.width
                    * self._camera._semiheight
                    + self._camera._focal_vector,
                )
                current = None
                for i in range(self._camera._max_reflect):
                    # dist, reflection, obj
                    closest = (math.inf, reflection, current)
                    for obj in self._objects:
                        if obj is current:
                            continue
                        tentative = obj.reflect(reflection)
                        if tentative.pos is None:
                            continue
                        dist = reflection._pos.distance_to(tentative.pos)
                        if dist < closest[0]:
                            closest = (dist, tentative, obj)
                    reflection = closest[1]
                    current = closest[2]
                    if math.isinf(closest[0]) or reflection._vector is None:
                        break
                surf.set_at((x, y), reflection._color)

