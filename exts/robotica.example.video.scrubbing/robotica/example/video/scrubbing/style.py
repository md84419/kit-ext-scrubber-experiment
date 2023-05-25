from omni.ui import color as cl

PADDING = 6.0
BORDER_RADIUS = 4.0

STYLE = {
    "VStack": {"margin": 10.0},
    # "ImageWithProvider": {"margin": PADDING, "border_width": 0.5, "border_radius": BORDER_RADIUS, "border_color": cl("0000007F")},
    # "ImageWithProvider:::hovered": {"border_width": 0, "border_radius": BORDER_RADIUS, "border_color": "black"},
    "ImageWithProvider": {"margin": PADDING},
    "Rectangle": {"padding_top": 200, "background_color": cl("#FF000000")},
    "Rectangle:::hovered": {"border_width": 1.8, "border_radius": BORDER_RADIUS, "border_color": "red"},
    "Line": {"margin": PADDING, "border_width": 1, "color": "red"},
}
