import logging
import asyncio
from pywizlight import wizlight, PilotBuilder
from WizLightingDefsHelpers import _create_bulb_steps, run_bulb_steps
import time
import random
from fractions import Fraction
import math
import copy
from pywizlight import wizlight, PilotBuilder
from wiz_lighting_config import CURRENT_DEFAULT_COLORS, RAINBOW_COLORS, BLUE_PINK_COLORS, MIN_FADE_TIME, DEFAULT_OFF_TIME, DEFAULT_HOLD_TIME, DEFAULT_FADE_TIME


def update_config(lamp_configz, updates):
    for key in updates:
        if key in lamp_configz:
            for keyy in updates[key]:
                lamp_configz[key][keyy] = updates[key][keyy]
    return lamp_configz

def make_colors_special(lamp_config):   
    colors = _extend_colors_with_duplication(
                _extend_colors_with_reverse(
                    _insert_offs_after_each_color(lamp_config["colors"], offs_after_each_color=1/3, multiply_colors=True),
                add_reverse=False), 
              duplication_factor=1)
              
    # Assign a lambda function to 'hold_time' that will be evaluated later
    colors = add_value_to_each_color(colors, update_existing=True, off_time=0, hold_time=lambda: random.randint(1,10)*0.05, fade_time=0.01)
    return colors
def make_steps_w_colors(lamp_config, colors=None, bulb_shift=None):
    if colors is None: 
        colors = lamp_config["colors"]
    if bulb_shift is None: 
        bulb_shift = lamp_config["bulb_shift"]


    steps_1 = _create_steps(len(lamp_config["ips"]), colors, bulb_shift)

    steps_1 = _add_off_after_everything_steps(
               _reverse_steps(steps_1, do_reverse=False), 
                len(lamp_config["ips"]), add_off_after_everything=False)
    
    return steps_1

def gradient_then_pause(lamp_config,gradient_steps_override=None):
    if gradient_steps_override is None: gradient_steps = len(lamp_config["ips"])-1 
    else: gradient_steps = gradient_steps_override

    colors_1=[]
    temp_colors=lamp_config["colors"]
    colors_2 = [temp_colors[0] for i in range(len(lamp_config["ips"])-1)]
    if len(temp_colors)>1:
        for color1,color2 in zip(temp_colors[:-1], temp_colors[1:]):
            colors_2.extend(make_gradient_between_each_color([color1,color2], gradient_steps=gradient_steps))
            colors_2.extend([color2 for i in range(len(lamp_config["ips"])-2)])
        colors_2.append(colors_2[-1])
    for color in colors_2:
        print(color)
    colors_2=add_value_to_each_color(colors_2, update_existing=True, off_time=0, hold_time=0.2, fade_time=0.01)
    return colors_2

def gradient_no_pause(lamp_config,gradient_steps_override=None):
    if gradient_steps_override is None: gradient_steps = len(lamp_config["ips"]) 
    else: gradient_steps = gradient_steps_override
    colors_1=[]
    temp_colors=lamp_config["colors"]
    colors_2 = [temp_colors[0] for i in range(1)]
    if len(temp_colors)>1:
        for color1,color2 in zip(temp_colors[:-1], temp_colors[1:]):
            colors_2.extend(make_gradient_between_each_color([color1,color2], gradient_steps=gradient_steps))
        colors_2.append(colors_2[-1])
    colors_2=add_value_to_each_color(colors_2, update_existing=True, off_time=0, hold_time=0.2, fade_time=0.01)
    return colors_2

async def messing_around_with_gradients_20250221():
    lamp_configs["playroom_fan"]["colors"]= copy.deepcopy(CURRENT_DEFAULT_COLORS)
    lamp_configs["dining"]["colors"]= copy.deepcopy(CURRENT_DEFAULT_COLORS)
#setting some gradient then pause action
    #lamp_configs["playroom_fan"]["colors"]=add_value_to_each_color(_extend_colors_with_reverse(gradient_then_pause(lamp_configs["playroom_fan"],gradient_steps_override=6)), 
    #update_existing=True, off_time=0, hold_time=0.1, fade_time=0.01)
    #lamp_configs["dining"]["colors"]=add_value_to_each_color(_extend_colors_with_reverse(gradient_then_pause(lamp_configs["dining"])), 
    #update_existing=True, off_time=0, hold_time=0.2, fade_time=0.01)
#setting some gradient no pause action
    lamp_configs["playroom_fan"]["bulb_shift"]=1
    lamp_configs["dining"]["bulb_shift"]=1
    lamp_configs["playroom_fan"]["colors"]=_extend_colors_with_duplication(_extend_colors_with_reverse(gradient_no_pause(lamp_configs["playroom_fan"],gradient_steps_override=6)),duplication_factor=2)
    lamp_configs["dining"]["colors"]=_extend_colors_with_duplication(_extend_colors_with_reverse(gradient_no_pause(lamp_configs["dining"])),duplication_factor=0)
    #now replace the colors for each step with random r g b values
    #for i in range(len(lamp_configs["playroom_fan"]["colors"])):
    #    rando=random.randint(0, 2)
    #    lamp_configs["playroom_fan"]["colors"][i]["r"] = 255 if rando == 0 else 0
    #    lamp_configs["playroom_fan"]["colors"][i]["g"] = 255 if rando == 1 else 0
    #    lamp_configs["playroom_fan"]["colors"][i]["b"] = 255 if rando == 2 else 0
    #for i in range(len(lamp_configs["dining"]["colors"])):
    #    rando=random.randint(0, 2)
    #    lamp_configs["dining"]["colors"][i]["r"] = 255 if rando == 0 else 0
    #    lamp_configs["dining"]["colors"][i]["g"] = 255 if rando == 1 else 0
    #    lamp_configs["dining"]["colors"][i]["b"] = 255 if rando == 2 else 0
    #this looks fun, rotating 1 off with the rest on and the gradient window set the same as the off window. even more fun if you turn off bulb_shift and turn on async_groups="bulbs"
    
    lamp_configs["playroom_fan"]["colors"]=add_value_to_each_color(
        _insert_offs_after_each_color(
            lamp_configs["playroom_fan"]["colors"]
            ,offs_after_each_color=1/3,multiply_colors=True)
            , 
    update_existing=True, off_time=0.01, hold_time=0.2, fade_time=0)
    lamp_configs["dining"]["colors"]=add_value_to_each_color(
        _insert_offs_after_each_color(
            lamp_configs["dining"]["colors"]
            ,offs_after_each_color=1/5,multiply_colors=True)
            , 
    update_existing=True, off_time=0.01, hold_time=0.2, fade_time=0)


    while True:
        tasks = [   asyncio.create_task(_run_bulbs(lamp_config, _create_steps(len(lamp_config["ips"]), lamp_config["colors"], lamp_config["bulb_shift"]), random_color_check=0, async_groups="bulbs"))   for lamp_config in lamp_configs.values()]

        for t in tasks:
            t.add_done_callback(lambda t: logging.error("Lamp group finished unexpectedly"))
        # Instead of waiting on all tasks to finish (which may never happen), block indefinitely.
        await asyncio.Event().wait()


def _create_steps(num_bulbs, colors, bulb_shift=0):
    steps = []
    for step_index in range(len(colors)):
        step = _create_bulb_steps(num_bulbs, colors, step_index, bulb_shift)
        steps.append(step)
        print(step)
    return steps


def _extend_colors_with_duplication(colors, duplication_factor=2):
    if duplication_factor > 1:
        colors_old = colors[:]  # Create a copy to iterate over
        colors = []
        for color in colors_old:
            colors.extend([color] * duplication_factor)
    return colors

def _extend_colors_with_reverse(colors, add_reverse=True):
    if add_reverse:
        reversed_colors = colors[1:-1][::-1]  # Reverse excluding first and last
        colors.extend(reversed_colors)
    return colors

def _insert_offs_after_each_color(colors, offs_after_each_color=1, multiply_colors=False):
    if offs_after_each_color > 0:
        # Handle fractional value exactly.
        if isinstance(offs_after_each_color, float) and offs_after_each_color < 1:
            frac = Fraction(offs_after_each_color).limit_denominator()  # e.g., Fraction(1,3)
            period = frac.denominator  # For 1/3, period will be 3.
            # If requested, multiply color pool to achieve an exact ratio.
            if multiply_colors:
                orig = list(colors)  # capture original colors
                colors = orig * period  # e.g., 7*3 = 21 colors
            original_len = len(colors)
            # Pre-calculate all insertion indices based on current length.
            indices = [i for i in range(period, original_len + 1, period)]
            print(f"DEBUG: offs fraction {offs_after_each_color} -> period {period}, original_len {original_len}, insertion indices: {indices}")
            # Insert off steps at the pre-calculated indices in reverse order.
            for idx in reversed(indices):
                print(f"DEBUG: Inserting Off at index {idx}")
                colors.insert(idx, {"name": "Off", "r": 0, "g": 0, "b": 0})
            print(f"DEBUG: Final colors count after fractional insertion: {len(colors)}")
        else:
            # For int or >=1 values, insert off steps after each color accordingly.
            for i in range(len(colors)-1, -1, -1):
                for _ in range(int(offs_after_each_color)):
                    print(f"DEBUG: Inserting Off at index {i+1}")
                    colors.insert(i + 1, {"name": "Off", "r": 0, "g": 0, "b": 0})
    return colors

def _add_off_after_everything_steps(steps, num_bulbs, add_off_after_everything=1):
    new_steps = []
    if add_off_after_everything:
        for step in steps:
            off_step = []
            for bulb_index in range(num_bulbs):
                current_off_time = step[bulb_index].get("off_time", DEFAULT_OFF_TIME)
                current_hold_time = step[bulb_index].get("hold_time", DEFAULT_HOLD_TIME)
                current_fade_time = step[bulb_index].get("fade_time", DEFAULT_FADE_TIME)
                # Debug print to show current time values for troubleshooting.
                print(f"Debug: bulb_index {bulb_index} -> off_time: {current_off_time}, hold_time: {current_hold_time}, fade_time: {current_fade_time}")
                off_step.append({
                    "name": "Off",
                    "r": 0,
                    "g": 0,
                    "b": 0,
                    "cw": 0,
                    "ww": 0,
                    "hold": current_off_time,
                    "fade": current_fade_time
                })
            new_steps.append(off_step)
            new_steps.append(step)
    else:
        new_steps = steps
    return new_steps

def _reverse_steps(steps, do_reverse=True):
    if do_reverse:
        reversed_steps = steps[:-1][::-1]  # Reverse all steps except the last one
        steps.extend(reversed_steps)
    return steps


async def _run_bulbs(lamp_config, steps, random_color_check=0, async_groups="steps"):
    bulbs = [wizlight(ip) for ip in lamp_config["ips"]]
    check_brightness_each_step = lamp_config["check_brightness_each_step"]
    check_brightness_first_step = lamp_config["check_brightness_first_step"]
    loopName = lamp_config["loopName"]
    initial_brightness = lamp_config["initial_brightness"]
    max_loop = lamp_config["max_loop"]

    brightness = None
    state = None
    states = [None] * len(bulbs)
    brightnesses = [None] * len(bulbs)
    loop_count = 0
    start_time = time.time()
    # Use concurrent state updates for the first step:
    if check_brightness_first_step:
        states = await asyncio.gather(*(b.updateState() for b in bulbs))
        for bulb_index, state in enumerate(states):
            brightnesses[bulb_index] = state.get_brightness() if state else initial_brightness
            if brightnesses[bulb_index] is None:
                logging.warning(f"Loop 1 Pre: Bulb {bulbs[bulb_index].ip}: Could not get current state, using initial brightness {initial_brightness}")
                brightnesses[bulb_index] = initial_brightness
            else:
                logging.info(f"Loop 1 Pre: Bulb {bulbs[bulb_index].ip}: Current brightness is {brightnesses[bulb_index]}")
    else:
        brightnesses = [initial_brightness] * len(bulbs)
        logging.info(f"Loop 1 Pre: Initial brightness is {initial_brightness}")
    
    last_colors = [None] * len(bulbs)  # Store the last color set for each bulb

    while loop_count < max_loop:
        loop_count += 1
        if async_groups == "steps":
            for step_index in range(len(steps)):
                tasks = []
                # Update brightness concurrently at each step if requested:
                if check_brightness_each_step:
                    states = await asyncio.gather(*(b.updateState() for b in bulbs))
                    for bulb_index, state in enumerate(states):
                        brightness = state.get_brightness() if state else brightnesses[bulb_index]
                        if brightness is not None and brightness != brightnesses[bulb_index]:
                            logging.info(f"Loop {loop_count} Step {step_index}: Bulb {bulbs[bulb_index].ip}: Brightness changed from {brightnesses[bulb_index]} to {brightness}")
                        brightnesses[bulb_index] = brightness if brightness is not None else brightnesses[bulb_index]
                for bulb_index, bulb in enumerate(bulbs):
                    bulb_steps = [steps[step_index][bulb_index]]
                    
                    if random_color_check > 0:
                        # Extract color information from the step
                        color_data = steps[step_index][bulb_index]
                        r, g, b = color_data.get("r", 0), color_data.get("g", 0), color_data.get("b", 0)
                        last_colors[bulb_index] = (r, g, b)  # Update last_colors with the current color
                    
                    tasks.append(run_bulb_steps(bulb, bulb_steps, brightnesses[bulb_index]))
                await asyncio.gather(*tasks)

                # Check if colors match every random_color_check steps
                if random_color_check > 0 and (loop_count * len(steps) + step_index + 1) % random_color_check == 0:
                    for bulb_index, bulb in enumerate(bulbs):
                        try:
                            state = await bulb.updateState()
                            current_rgb = state.get_rgb()
                            if current_rgb != last_colors[bulb_index]:
                                logging.warning(f"Loop {loop_count} Step {step_index + 1}: Bulb {bulb.ip} color mismatch. Expected {last_colors[bulb_index]}, got {current_rgb}")
                        except Exception as e:
                            logging.error(f"Error getting state for bulb {bulb.ip}: {e}")
                    print(f"Loop {loopName} Step {step_index + 1}: Colors match.")
        elif async_groups == "bulbs":
            tasks = []
            for bulb_index, bulb in enumerate(bulbs):
                # Update brightness before each bulb's steps if requested
                if check_brightness_each_step:
                    states = await bulb.updateState()
                    brightness = states.get_brightness() if states else brightnesses[bulb_index]
                    if brightness is not None and brightness != brightnesses[bulb_index]:
                        logging.info(f"Loop {loop_count}: Bulb {bulb.ip}: Brightness changed from {brightnesses[bulb_index]} to {brightness}")
                    brightnesses[bulb_index] = brightness if brightness is not None else brightnesses[bulb_index]
                
                bulb_steps = [steps[step_index][bulb_index] for step_index in range(len(steps))]
                
                async def run_all_steps_for_bulb(bulb, bulb_steps, brightness, bulb_index):
                    for step_index, step in enumerate(bulb_steps):
                        if random_color_check > 0:
                            # Extract color information from the step
                            color_data = steps[step_index][bulb_index]
                            r, g, b = color_data.get("r", 0), color_data.get("g", 0), color_data.get("b", 0)
                            last_colors[bulb_index] = (r, g, b)  # Update last_colors with the current color
                        await run_bulb_steps(bulb, [step], brightness)
                        # Check if colors match every random_color_check steps
                        if random_color_check > 0 and (loop_count * len(bulb_steps) + step_index + 1) % random_color_check == 0:
                            try:
                                state = await bulb.updateState()
                                current_rgb = state.get_rgb()
                                if current_rgb != last_colors[bulb_index]:
                                    logging.warning(f"Loop {loop_count} Step {step_index + 1}: Bulb {bulb.ip} color mismatch. Expected {last_colors[bulb_index]}, got {current_rgb}")
                            except Exception as e:
                                logging.error(f"Error getting state for bulb {bulb.ip}: {e}")
                        print(f"Loop {loopName} Step {step_index + 1}: Colors match.")
                
                tasks.append(run_all_steps_for_bulb(bulb, bulb_steps, brightnesses[bulb_index], bulb_index))
            await asyncio.gather(*tasks)
        elif async_groups == "neither":
            for step_index in range(len(steps)):
                # Update brightness concurrently at each step if requested:
                if check_brightness_each_step:
                    states = await asyncio.gather(*(b.updateState() for b in bulbs))
                    for bulb_index, state in enumerate(states):
                        brightness = state.get_brightness() if state else brightnesses[bulb_index]
                        if brightness is not None and brightness != brightnesses[bulb_index]:
                            logging.info(f"Loop {loop_count} Step {step_index}: Bulb {bulbs[bulb_index].ip}: Brightness changed from {brightnesses[bulb_index]} to {brightness}")
                        brightnesses[bulb_index] = brightness if brightness is not None else brightnesses[bulb_index]
                for bulb_index, bulb in enumerate(bulbs):
                     bulb_steps = [steps[step_index][bulb_index]]
                     if random_color_check > 0:
                        # Extract color information from the step
                        color_data = steps[step_index][bulb_index]
                        r, g, b = color_data.get("r", 0), color_data.get("g", 0), color_data.get("b", 0)
                        last_colors[bulb_index] = (r, g, b)  # Update last_colors with the current color
                     await run_bulb_steps(bulb, bulb_steps, brightnesses[bulb_index])
                     if random_color_check > 0 and (loop_count * len(steps) + step_index + 1) % random_color_check == 0:
                        try:
                            state = await bulb.updateState()
                            current_rgb = state.get_rgb()
                            if current_rgb != last_colors[bulb_index]:
                                logging.warning(f"Loop {loop_count} Step {step_index + 1}: Bulb {bulb.ip} color mismatch. Expected {last_colors[bulb_index]}, got {current_rgb}")
                        except Exception as e:
                            logging.error(f"Error getting state for bulb {bulb.ip}: {e}")
                     print(f"Loop {loopName} Step {step_index + 1}: Colors match.")
        else:
            raise ValueError("Invalid async_groups value. Must be 'steps', 'bulbs', or 'neither'.")

        elapsed_time = time.time() - start_time
        print(f"Loop {loopName} Number {loop_count}: Elapsed time = {elapsed_time:.2f} seconds")
        loop_count += 1



def add_value_to_each_color(colors, update_existing=True, **kwargs):
    """
    Updates each color (a dictionary) in the list with the provided key-value pairs.
    
    If update_existing is False, the function keeps the current value 
    if the key already exists in the color dictionary.
    
    For example:
       add_value_to_each_color(colors, update_or_keep=False, off_time=0, hold_time=0.1)
    """
    for color in colors:
        for key, value in kwargs.items():
            if update_existing or key not in color:
                color[key] = value
    return colors

def off_to_blue_and_on_to_red(colors):
    """
    Transforms each color in the list:
    - Colors with (r, g, b) all 0 become Blue.
    - All other colors become Red.
    
    Args:
        colors (list): List of color dictionaries, each with keys "name", "r", "g", "b".
        
    Returns:
        list: New list of transformed color dictionaries.
    """
    new_colors = []
    for color in colors:
        if color.get("r") == 0 and color.get("g") == 0 and color.get("b") == 0:
            # All zero, make blue.
            new_colors.append({"name": "Blue", "r": 0, "g": 0, "b": 255})
        else:
            # Otherwise, make red.
            new_colors.append({"name": "Red", "r": 255, "g": 0, "b": 0})
    return new_colors


def make_gradient_between_each_color(colors, max_step=255, gradient_steps=0):
        new_colors = []
        for i in range(len(colors) - 1):
            color1 = colors[i]
            color2 = colors[i + 1]
            r_diff = color2["r"] - color1["r"]
            g_diff = color2["g"] - color1["g"]
            b_diff = color2["b"] - color1["b"]
            new_colors.append(color1)
            temp_color = color1.copy()  # Start with a copy of color1
            if gradient_steps>0:
                for i in range(gradient_steps):
                    temp_color = {"r": int(color1["r"] + ((i+1) * r_diff / gradient_steps)),
                                "g": int(color1["g"] + ((i+1) * g_diff  / gradient_steps)),
                                 "b": int(color1["b"] + ((i+1) * b_diff / gradient_steps))}
                    new_colors.append(temp_color.copy())  # Append a copy of the modified color
            else:
                while temp_color["r"] != color2["r"] or temp_color["g"] != color2["g"] or temp_color["b"] != color2["b"]:
                    if temp_color["r"] < color2["r"]:
                        temp_color["r"] += min(max_step, color2["r"] - temp_color["r"] )
                    elif temp_color["g"] < color2["g"]:
                        temp_color["g"] += min(max_step, color2["g"] - temp_color["g"])
                    elif temp_color["b"] < color2["b"]:
                        temp_color["b"] += min(max_step, color2["b"] - temp_color["b"])
                    elif temp_color["r"] > color2["r"]:
                        temp_color["r"] -= min(max_step, temp_color["r"] - color2["r"])
                    elif temp_color["g"] > color2["g"]:
                        temp_color["g"] -= min(max_step, temp_color["g"] - color2["g"])
                    elif temp_color["b"] > color2["b"]:
                        temp_color["b"] -= min(max_step, temp_color["b"] - color2["b"])
                    if (temp_color["r"] != color2["r"] or temp_color["g"] != color2["g"] or temp_color["b"] != color2["b"]):
                        new_colors.append(temp_color.copy())  # Append a copy of the modified color if it is not the final color
        new_colors.append(colors[-1]) #append the last color
        return new_colors


