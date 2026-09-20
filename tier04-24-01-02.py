# Too Tall Toby: "24-01-02".
#
# A clevis bracket: a slotted base plate with a dovetail groove underneath and
# two bored ears standing on it. All dimensions are in millimeters.

import math

from build123d import (
    Align,
    BuildLine,
    BuildPart,
    BuildSketch,
    CenterArc,
    Circle,
    Line,
    Locations,
    Mode,
    Plane,
    Polyline,
    RectangleRounded,
    SlotOverall,
    extrude,
    make_face,
)

BASE_LENGTH = 118.0  # overall length of the base plate
BASE_WIDTH = 54.0  # overall width of the base plate
BASE_THICKNESS = 16.0  # thickness of the base plate
BASE_CORNER_RADIUS = 6.0  # the four rounded corners of the base plate

SLOT_LENGTH = 99.0  # overall length of the slot, rounded ends included
SLOT_WIDTH = 16.0
SLOT_TO_END = 9.0  # from the right end of the base plate to the slot

GROOVE_WIDTH = 22.0  # width of the dovetail groove where it opens up
GROOVE_DEPTH = 8.0
GROOVE_ANGLE = 60.0  # between a flank of the groove and the bottom face

EAR_THICKNESS = 14.0  # each of the two ears
BOSS_DIAMETER = 55.0  # the round top of an ear
BOSS_HEIGHT = 42.0  # from the bottom face up to the axis of the bore
FILLET_RADIUS = 12.0  # where an ear runs into the base plate
BORE_DIAMETER = 30.0  # through both ears
COUNTERBORE_DIAMETER = 38.0  # in the outer face of each ear
COUNTERBORE_DEPTH = 4.0

boss_radius = BOSS_DIAMETER / 2.0

# The fillet that blends an ear into the top face of the base plate touches
# both the boss and that face, so its center is one fillet radius above the
# face and one boss-plus-fillet radius away from the axis of the bore.
fillet_center_z = BASE_THICKNESS + FILLET_RADIUS
fillet_center_x = boss_radius + math.sqrt((boss_radius + FILLET_RADIUS) ** 2 - (fillet_center_z - BOSS_HEIGHT) ** 2)
# The fillet meets the boss on the line between the two centers, so that
# direction is where the arc around the boss has to stop.
tangent_angle = math.degrees(math.atan2(fillet_center_z - BOSS_HEIGHT, fillet_center_x - boss_radius))

with BuildPart() as bracket:
    # --- the base plate, with its slot and its dovetail groove ---------------
    with BuildSketch(Plane.XY):
        RectangleRounded(
            BASE_LENGTH,
            BASE_WIDTH,
            BASE_CORNER_RADIUS,
            align=(Align.MIN, Align.CENTER),
        )
        with Locations((BASE_LENGTH - SLOT_TO_END - SLOT_LENGTH / 2.0, 0.0)):
            SlotOverall(SLOT_LENGTH, SLOT_WIDTH, mode=Mode.SUBTRACT)
    extrude(amount=BASE_THICKNESS)

    # The groove runs the whole length of the plate and widens as it goes up.
    groove_overhang = GROOVE_DEPTH / math.tan(math.radians(GROOVE_ANGLE))
    with BuildSketch(Plane.YZ):
        with BuildLine():
            Polyline(
                (-GROOVE_WIDTH / 2.0, 0.0),
                (GROOVE_WIDTH / 2.0, 0.0),
                (GROOVE_WIDTH / 2.0 + groove_overhang, GROOVE_DEPTH),
                (-GROOVE_WIDTH / 2.0 - groove_overhang, GROOVE_DEPTH),
                close=True,
            )
        make_face()
    extrude(amount=BASE_LENGTH, mode=Mode.SUBTRACT)

    # --- the two ears -------------------------------------------------------
    # Seen from the side an ear is a round boss carried on a straight back,
    # running into the base plate through a tangent fillet.
    for plane in (Plane.XZ.offset(-BASE_WIDTH / 2.0), Plane.XZ.offset(BASE_WIDTH / 2.0 - EAR_THICKNESS)):
        with BuildSketch(plane):
            with BuildLine():
                Line((0.0, BASE_THICKNESS), (0.0, BOSS_HEIGHT))
                CenterArc(
                    (boss_radius, BOSS_HEIGHT),
                    boss_radius,
                    180.0,
                    tangent_angle - 180.0,
                )
                CenterArc(
                    (fillet_center_x, fillet_center_z),
                    FILLET_RADIUS,
                    tangent_angle + 180.0,
                    270.0 - (tangent_angle + 180.0),
                )
                Line((fillet_center_x, BASE_THICKNESS), (0.0, BASE_THICKNESS))
            make_face()
        extrude(amount=EAR_THICKNESS)

    # --- the bore and its two counterbores ----------------------------------
    with BuildSketch(Plane.XZ.offset(-BASE_WIDTH / 2.0)):
        with Locations((boss_radius, BOSS_HEIGHT)):
            Circle(BORE_DIAMETER / 2.0)
    extrude(amount=BASE_WIDTH, mode=Mode.SUBTRACT)

    for plane in (Plane.XZ.offset(-BASE_WIDTH / 2.0), Plane.XZ.offset(BASE_WIDTH / 2.0).reverse()):
        with BuildSketch(plane):
            with Locations((boss_radius, BOSS_HEIGHT)):
                Circle(COUNTERBORE_DIAMETER / 2.0)
        extrude(amount=COUNTERBORE_DEPTH, mode=Mode.SUBTRACT)

show_object(bracket.part)
