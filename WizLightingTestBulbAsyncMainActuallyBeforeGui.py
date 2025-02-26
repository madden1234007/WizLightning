import math
import asyncio
import time
import random
import logging
import copy
from pywizlight import wizlight, PilotBuilder
from WizLightingDefs import  _create_steps, _extend_colors_with_duplication, \
    _extend_colors_with_reverse, _insert_offs_after_each_color, \
    _add_off_after_everything_steps, _reverse_steps, _run_bulbs, add_value_to_each_color, \
    off_to_blue_and_on_to_red, make_gradient_between_each_color, init_devices, init_colors, \
   make_colors_special, make_steps_w_colors, current_best
from wiz_lighting_config import DEFAULT_HOLD_TIME_RANGE, DEFAULT_OFF_TIME, DEFAULT_FADE_TIME, MIN_FADE_TIME, RAINBOW_COLORS, DIVERSE_COLORS, BLUE_COLORS, BLUE_PINK_COLORS, CURRENT_DEFAULT_COLORS
from wiz_extended_colors import define_dynamic_colors



async def main():
    #logging.basicConfig(level=logging.DEBUG) #this is a debug level, we might want to change to INFO or WARNING
    logging.basicConfig(level=logging.INFO)
    init_devices() #Initialize devices from config file
    #init_colors() This is no longer needed.
    define_dynamic_colors() #initialize dynamic colors
    lamp_configs=await current_best()


if __name__ == "__main__":
    asyncio.run(main())

