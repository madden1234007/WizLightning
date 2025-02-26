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
    off_to_blue_and_on_to_red, make_gradient_between_each_color, \
   make_colors_special, make_steps_w_colors, update_config
from wiz_lighting_default_device_config import ips
from wiz_lighting_config import DEFAULT_HOLD_TIME, DEFAULT_HOLD_TIME_RANGE, DEFAULT_OFF_TIME, DEFAULT_FADE_TIME, MIN_FADE_TIME, RAINBOW_COLORS, DIVERSE_COLORS, BLUE_COLORS, BLUE_PINK_COLORS, CURRENT_DEFAULT_COLORS, make_default_config_dict
from wiz_extended_colors import define_dynamic_colors



def init_devices():
    ipz=ips()
    lamp_configs={}
    for name in ipz.keys():
        lamp_configs[name] = make_default_config_dict(name, ipz[name])
    
    return lamp_configs

def after_init_devices_1(lamp_configs):
    
    lamp_configs=update_config(lamp_configs,{
            "dining": {
                "initial_brightness": 90,
                "bulb_shift": 1,
                "check_brightness_each_step": True,
                "check_brightness_first_step": True,
                "colors": copy.deepcopy(RAINBOW_COLORS), #RAINBOW_COLORS
                "hold_time": lambda: 2*int(random.randint(0,1)*0.05),
            },
            "playroom_fan": {
                "initial_brightness": 50,
                "bulb_shift": 0,
                "check_brightness_each_step": True,
                "check_brightness_first_step": False,
                "colors": copy.deepcopy(RAINBOW_COLORS), #RAINBOW_COLORS
                "hold_time": lambda: 2*int(random.randint(0,1)*0.05),
            }
        }
    )
    return lamp_configs

def after_init_devices_2(lamp_configs):
    
    pr_fan_colors=add_value_to_each_color(
        _extend_colors_with_reverse(copy.deepcopy(BLUE_PINK_COLORS)), update_existing=True, off_time=0.01, hold_time=0.5, fade_time=3)
    lamp_configs=update_config(lamp_configs,
    {
        "playroom_fan": {
            "colors": pr_fan_colors,
            "initial_brightness": 100
        },
        "dining": {
            "bulb_shift": 1,
            "colors": add_value_to_each_color(copy.deepcopy(DIVERSE_COLORS), update_existing=True, off_time=0.01, hold_time=1.25, fade_time=1.25)
        }


    })

    return lamp_configs


async def main():
    #logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    lamp_configs = init_devices() #Initialize devices from config file
    define_dynamic_colors() #initialize dynamic colors if you need them
    lamp_configs = after_init_devices_2(lamp_configs)
    
    while True:
        tasks = [   asyncio.create_task(_run_bulbs(lamp_config, _create_steps(len(lamp_config["ips"]), lamp_config["colors"], lamp_config["bulb_shift"]), random_color_check=0, async_groups="steps"))   for lamp_config in lamp_configs.values()]

        for t in tasks:
            t.add_done_callback(lambda t: logging.error("Lamp group finished unexpectedly"))
        # Instead of waiting on all tasks to finish (which may never happen), block indefinitely.
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())

