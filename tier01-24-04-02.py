# Too Tall Toby: "24-04-02".
#
# A plumb bob: a chamfered cylinder over a cone, with a cross hole.
# The drawing is in inches; the model is in millimeters, as PartCAD expects.

import math

from build123d import (
    Axis,
    BuildLine,
    BuildPart,
    BuildSketch,
    Circle,
    Locations,
    Mode,
    Plane,
    Polyline,
    extrude,
    make_face,
    revolve,
)

INCH = 25.4

HEIGHT = 3.500 * INCH  # overall, from the tip to the top face
BODY_DIAMETER = 1.500 * INCH
SHOULDER_DIAMETER = 1.250 * INCH  # where the chamfer starts, on a flat annulus
TOP_DIAMETER = 1.000 * INCH  # the flat on top
CHAMFER_HEIGHT = 0.125 * INCH  # the chamfer stands 135 degrees off the top face
TIP_DIAMETER = 0.375 * INCH  # the cone is cut off flat here
CONE_ANGLE = 33.0  # degrees, between the two sides of the cone
HOLE_DIAMETER = 0.500 * INCH  # across the body
HOLE_BELOW_TOP = 0.750 * INCH  # from the top face down to the axis of the hole

body_radius = BODY_DIAMETER / 2.0
tip_radius = TIP_DIAMETER / 2.0
# The cone is as tall as its angle and the two diameters make it.
cone_height = (body_radius - tip_radius) / math.tan(math.radians(CONE_ANGLE / 2.0))
shoulder_height = HEIGHT - CHAMFER_HEIGHT

with BuildPart() as plumb_bob:
    # Half of the outline, turned about the axis.
    with BuildSketch(Plane.XZ):
        with BuildLine():
            Polyline(
                (0.0, 0.0),
                (tip_radius, 0.0),
                (body_radius, cone_height),
                (body_radius, shoulder_height),
                (SHOULDER_DIAMETER / 2.0, shoulder_height),
                (TOP_DIAMETER / 2.0, HEIGHT),
                (0.0, HEIGHT),
                close=True,
            )
        make_face()
    revolve(axis=Axis.Z)

    # The cross hole, drilled through the cylindrical part of the body.
    with BuildSketch(Plane.XZ.offset(-body_radius)):
        with Locations((0.0, HEIGHT - HOLE_BELOW_TOP)):
            Circle(HOLE_DIAMETER / 2.0)
    extrude(amount=BODY_DIAMETER, mode=Mode.SUBTRACT)

show_object(plumb_bob.part)
