# Too Tall Toby: "24-01-03".
#
# A molded cup: a closed dome over a drafted cavity, with a swept handle.
# All dimensions are in millimeters.

import math

from build123d import (
    Axis,
    BuildLine,
    BuildPart,
    BuildSketch,
    CenterArc,
    Ellipse,
    EllipticalCenterArc,
    Mode,
    Plane,
    Polyline,
    fillet,
    make_face,
    revolve,
    sweep,
)

OUTER_DIAMETER = 50.0  # the body is a straight cylinder on the outside
HEIGHT = 55.0  # overall, up to the top of the dome
DOME_HEIGHT = 8.0  # the elliptical dome over the closed end
DOME_FLAT_DIAMETER = 10.0  # where the dome flattens out on top

CAVITY_DIAMETER = 42.0  # at the open end
CAVITY_DEPTH = 42.0
CAVITY_DRAFT = 3.0  # degrees; the cavity narrows towards the closed end
CAVITY_FILLET = 4.0  # at the closed end of the cavity

HANDLE_BOTTOM = 4.0  # where the handle runs into the body
HANDLE_TOP = 41.0
HANDLE_REACH = 34.0  # from the axis to the outside of the handle
HANDLE_SECTION_DEPTH = 6.0  # of the section, across the sweep
HANDLE_SECTION_WIDTH = 12.0  # of the section, along the body
HANDLE_EMBED = 2.0  # how far the sweep is buried in the wall at each end

outer_radius = OUTER_DIAMETER / 2.0
dome_start = HEIGHT - DOME_HEIGHT
dome_flat_radius = DOME_FLAT_DIAMETER / 2.0

# The handle is a constant elliptical section swept along a circular arc, so
# its outside is another arc about the same center -- one that leaves the body
# at HANDLE_BOTTOM, comes back to it at HANDLE_TOP, and reaches HANDLE_REACH
# half way up. Those three points are what fixes the center and the radii.
handle_center_z = (HANDLE_BOTTOM + HANDLE_TOP) / 2.0
handle_half_span = (HANDLE_TOP - HANDLE_BOTTOM) / 2.0
handle_center_x = (HANDLE_REACH**2 - outer_radius**2 - handle_half_span**2) / (2.0 * (HANDLE_REACH - outer_radius))
handle_path_radius = HANDLE_REACH - handle_center_x - HANDLE_SECTION_DEPTH / 2.0
# Run the sweep a little past the outside of the body at both ends, so that it
# is buried in the wall rather than ending on it.
handle_half_angle = math.degrees(math.acos((outer_radius - HANDLE_EMBED - handle_center_x) / handle_path_radius))

with BuildPart() as cup:
    # --- the body: a cylinder capped by an elliptical dome -------------------
    with BuildSketch(Plane.XZ):
        with BuildLine():
            Polyline((0.0, 0.0), (outer_radius, 0.0), (outer_radius, dome_start))
            # The dome runs from the wall to the flat on top: vertical where it
            # leaves the wall, horizontal where it arrives.
            EllipticalCenterArc(
                (dome_flat_radius, dome_start),
                outer_radius - dome_flat_radius,
                DOME_HEIGHT,
                start_angle=0.0,
                arc_size=90.0,
            )
            Polyline((dome_flat_radius, HEIGHT), (0.0, HEIGHT), (0.0, 0.0))
        make_face()
    revolve(axis=Axis.Z)

    # --- the handle ---------------------------------------------------------
    with BuildLine(Plane.XZ):
        CenterArc(
            (handle_center_x, handle_center_z),
            handle_path_radius,
            -handle_half_angle,
            2.0 * handle_half_angle,
        )
    start_x = handle_center_x + handle_path_radius * math.cos(math.radians(-handle_half_angle))
    start_z = handle_center_z + handle_path_radius * math.sin(math.radians(-handle_half_angle))
    # The section stands square to the path, with its long axis along the body.
    with BuildSketch(
        Plane(
            origin=(start_x, 0.0, start_z),
            x_dir=(0.0, 1.0, 0.0),
            z_dir=(
                -math.sin(math.radians(-handle_half_angle)),
                0.0,
                math.cos(math.radians(-handle_half_angle)),
            ),
        )
    ):
        Ellipse(HANDLE_SECTION_WIDTH / 2.0, HANDLE_SECTION_DEPTH / 2.0)
    sweep()

    # --- the cavity, drafted so the part can leave a mold --------------------
    # Cut last: it trims whatever the buried ends of the handle reach into.
    cavity_radius = CAVITY_DIAMETER / 2.0
    cavity_top_radius = cavity_radius - CAVITY_DEPTH * math.tan(math.radians(CAVITY_DRAFT))
    with BuildSketch(Plane.XZ) as cavity:
        with BuildLine():
            Polyline(
                (0.0, 0.0),
                (cavity_radius, 0.0),
                (cavity_top_radius, CAVITY_DEPTH),
                (0.0, CAVITY_DEPTH),
                close=True,
            )
        make_face()
        # The corner where the cavity closes is rounded off.
        closed_end = min(cavity.vertices(), key=lambda v: (v.X - cavity_top_radius) ** 2 + (v.Y - CAVITY_DEPTH) ** 2)
        fillet([closed_end], CAVITY_FILLET)
    revolve(axis=Axis.Z, mode=Mode.SUBTRACT)

show_object(cup.part)
