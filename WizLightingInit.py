#add imports required below
from wiz_lighting_default_device_config import ips
from wiz_lighting_config import make_default_config_dict

import copy
from WizLightingDefs import add_value_to_each_color, update_config, _extend_colors_with_reverse
from wiz_lighting_config import BLUE_PINK_COLORS, DIVERSE_COLORS


def init_devices():
    ipz=ips()
    lamp_configs={}
    for name in ipz.keys():
        lamp_configs[name] = make_default_config_dict(name, ipz[name])
    
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
