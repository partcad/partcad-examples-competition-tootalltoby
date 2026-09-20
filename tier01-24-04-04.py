# Too Tall Toby: "24-04-04".
#
# A cabinet pull: an arched bar whose top is one long radius.
# The drawing is in inches; the model is in millimeters, as PartCAD expects.

from build123d import (
    Axis,
    BuildLine,
    BuildPart,
    BuildSketch,
    Plane,
    Polyline,
    RadiusArc,
    Vertex,
    extrude,
    fillet,
    make_face,
)

INCH = 25.4

LENGTH = 10.000 * INCH  # overall
THICKNESS = 0.750 * INCH  # across the bar
LEFT_HEIGHT = 1.000 * INCH  # of the end face at the left
RIGHT_HEIGHT = 0.750 * INCH  # of the end face at the right
TOP_RADIUS = 18.000 * INCH  # the top runs from one end face to the other
LEFT_FOOT = 2.500 * INCH  # how much of the bar sits on the surface, each end
RIGHT_FOOT = 3.500 * INCH
GRIP_HEIGHT = 1.000 * INCH  # the opening under the bar
GRIP_RADIUS = 0.750 * INCH  # where the opening meets a foot
EDGE_RADIUS = 0.1875 * INCH  # along every edge of the two sides

with BuildPart() as pull:
    with BuildSketch(Plane.XZ) as side:
        with BuildLine():
            Polyline(
                (0.0, 0.0),
                (0.0, LEFT_HEIGHT),
            )
            RadiusArc((0.0, LEFT_HEIGHT), (LENGTH, RIGHT_HEIGHT), TOP_RADIUS)
            Polyline(
                (LENGTH, RIGHT_HEIGHT),
                (LENGTH, 0.0),
                (LENGTH - RIGHT_FOOT, 0.0),
                (LENGTH - RIGHT_FOOT, GRIP_HEIGHT),
                (LEFT_FOOT, GRIP_HEIGHT),
                (LEFT_FOOT, 0.0),
                (0.0, 0.0),
            )
        make_face()

        def corner(x: float, z: float) -> Vertex:
            return min(side.vertices(), key=lambda v: (v.X - x) ** 2 + (v.Y - z) ** 2)

        fillet(
            [corner(LEFT_FOOT, GRIP_HEIGHT), corner(LENGTH - RIGHT_FOOT, GRIP_HEIGHT)],
            GRIP_RADIUS,
        )
    extrude(amount=THICKNESS / 2.0, both=True)

    # Every edge that runs along the bar is broken the same way.
    fillet(pull.faces().filter_by(Axis.Y).edges(), EDGE_RADIUS)

show_object(pull.part)
