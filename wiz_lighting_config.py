"""
Configuration settings and constants for the Wiz lighting system.
"""

import random

# Constants
MAX_RGB_VALUE = 255
MIN_RGB_VALUE = 0

# Time and transition defaults
DEFAULT_HOLD_TIME_RANGE = (0, 0) #2*int(random.randint(0,0)*0.05)
DEFAULT_HOLD_TIME=random.randint(DEFAULT_HOLD_TIME_RANGE[0],DEFAULT_HOLD_TIME_RANGE[1])
DEFAULT_OFF_TIME = 0
DEFAULT_FADE_TIME = 0
MIN_FADE_TIME = 0.1

# Color palettes
RAINBOW_COLORS = [
    {"name": "Red", "r": 255, "g": 0, "b": 0},
    {"name": "Orange", "r": 255, "g": 127, "b": 0},
    {"name": "Yellow", "r": 255, "g": 255, "b": 0},
    {"name": "Green", "r": 0, "g": 255, "b": 0},
    {"name": "Teal", "r": 0, "g": 255, "b": 255},
    {"name": "Blue", "r": 0, "g": 0, "b": 255},
    {"name": "Indigo", "r": 75, "g": 0, "b": 130},
    {"name": "Violet", "r": 238, "g": 130, "b": 238},
]

DIVERSE_COLORS = [
    {"name": "Red", "r": 255, "g": 0, "b": 0},
    {"name": "Orange", "r": 255, "g": 70, "b": 0},
    {"name": "Yellow", "r": 255, "g": 255, "b": 0},
    {"name": "Green", "r": 0, "g": 255, "b": 0},
    {"name": "Teal", "r": 0, "g": 255, "b": 255},
    {"name": "Blue", "r": 0, "g": 0, "b": 255},
    {"r": 170, "g": 30, "b": 255, "name": "Purple"},
    {"r": 255, "g": 0, "b": 30, "name": "Neon Salmon"},
]

BLUE_COLORS = [
    {"name": "Blue", "r": 20, "g": 30, "b": 255},
    {"name": "LightSkyBlue", "r": 30, "g": 75, "b": 255},
    {"name": "LightCyan", "r": 30, "g": 75, "b": 238},
]
BLUE_PINK_COLORS = [
        {"name": "Teal",   "r": 20,   "g": 200, "b": 220},
        {"name": "Teal",   "r": 20,   "g": 200, "b": 200},
        {"name": "Teal",   "r": 30,   "g": 140, "b": 180},
        {"name": "Teal",   "r": 30,   "g": 140, "b": 140},
        {"r": 180, "g": 60, "b": 70, "name": "Salmon"}
    ]
CURRENT_DEFAULT_COLORS=DIVERSE_COLORS


def make_default_config_dict(name, ips):
    return {
    #required
            "loopName": name,
            "bulb_shift": 0,        
            "initial_brightness": 50,
            "max_loop": 99999,
            "ips": ips,
            "colors": [{"r": 255, "g": 255, "b": 255}],
    #default to None, but works:
            "check_brightness_each_step": True,
            "check_brightness_first_step": True,
    #pretty sure we dont need these since it reads config directly    
            #"off_time": DEFAULT_OFF_TIME,
            #"hold_time": DEFAULT_HOLD_TIME,
            #"fade_time": DEFAULT_FADE_TIME,
    }

