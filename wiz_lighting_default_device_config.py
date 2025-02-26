
def ips():
    ips={}
    ips["playroom_fan"]=["10.0.0.208","10.0.0.200","10.0.0.201","10.0.0.189","10.0.0.188","10.0.0.203","10.0.0.204","10.0.0.205","10.0.0.187","10.0.0.137","10.0.0.202","10.0.0.207","10.0.0.206"] #all 13 from left/right snaking,
    ips["dining"]=["10.0.0.181", "10.0.0.182", "10.0.0.183", "10.0.0.184", "10.0.0.185", "10.0.0.186","10.0.0.190","10.0.0.191"]
    return ips
    

def current_best_old_init():
    return {
        "dining": {
            "loopName": "dining",
            "ips": ["10.0.0.181", "10.0.0.182", "10.0.0.183", "10.0.0.184", "10.0.0.185", "10.0.0.186","10.0.0.190","10.0.0.191"],
            "initial_brightness": 90,
            "bulb_shift": 1,
            "check_brightness_each_step": True,
            "check_brightness_first_step": True,
            "max_loop": 999,
            "colors": copy.deepcopy(RAINBOW_COLORS), #RAINBOW_COLORS
            "off_time": 0,
            "hold_time": lambda: 2*int(random.randint(0,0)*0.05),
            "fade_time": 0,
        },
        "playroom_fan": {
            "loopName": "playroom_fan",
            "ips": ["10.0.0.208","10.0.0.200","10.0.0.201","10.0.0.189","10.0.0.188","10.0.0.203","10.0.0.204","10.0.0.205","10.0.0.187","10.0.0.137","10.0.0.202","10.0.0.207","10.0.0.206"], #all 13 from left/right snaking,
            "initial_brightness": 50,
            "bulb_shift": 0,
            "check_brightness_each_step": True,
            "check_brightness_first_step": False,
            "max_loop": 999,
            "colors": copy.deepcopy(RAINBOW_COLORS), #RAINBOW_COLORS
            "off_time": 0,
            "hold_time": lambda: 2*int(random.randint(0,0)*0.05),
            "fade_time": 0,
        }
    }  