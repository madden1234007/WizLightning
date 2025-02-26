import logging
import asyncio
from pywizlight import wizlight, PilotBuilder
import time
import random
from wiz_lighting_config import MIN_RGB_VALUE, MAX_RGB_VALUE, DEFAULT_HOLD_TIME, DEFAULT_OFF_TIME, DEFAULT_FADE_TIME, MIN_FADE_TIME


# Function to run the steps for a given bulb only
async def run_bulb_steps(bulb, bulb_steps, brightness):
    logging.debug(f"Starting run_bulb_steps for bulb {bulb.ip} with {len(bulb_steps)} step(s)")
    for idx, step in enumerate(bulb_steps):
        logging.debug(f"Bulb {bulb.ip}: Executing step {idx}: {step}")
        try:
            if step["r"] == 0 and step["g"] == 0 and step["b"] == 0:
                t0 = time.time()
                logging.info(f"Bulb {bulb.ip}: Turning off")
                await bulb.turn_off()
            else: 
                if step["fade"] > 0:
                    t1=time.time()
                    state = await bulb.updateState()
                    #initialize to 0 if not found
                    current_r, current_g, current_b = state.get_rgb()
                    if current_r is None: current_r=MIN_RGB_VALUE
                    if current_g is None: current_g=MIN_RGB_VALUE
                    if current_b is None: current_b=MIN_RGB_VALUE

                    print(f"current_r, current_g, current_b {current_r}, {current_g}, {current_b}")
                    #i want to make sure the fade doesnt take longer than the fade_time, even after updatingbulb
                    #calculate how many fade steps we can have given the time and that a step takes min 0.1 sec
                    fade_time = max(step["fade"] - (time.time() - t1),0)
                    fade_steps = int(max(1, fade_time / MIN_FADE_TIME))
                    #if step["fade_steps"] is not None: fade_steps = max(fade_steps,(step["fade_steps"])
                    for i in range(fade_steps):
                        t2 = time.time()
                        if t2 - t1 > step["fade"] and i > 0: break
                        else:
                            fade_r = int(current_r + (i + 1) * (step["r"] - current_r) / fade_steps)
                            fade_g = int(current_g + (i + 1) * (step["g"] - current_g) / fade_steps)
                            fade_b = int(current_b + (i + 1) * (step["b"] - current_b) / fade_steps)
                            pilot = PilotBuilder(rgbww=(fade_r, fade_g, fade_b, 0, 0), brightness=brightness)
                            logging.debug(f"Bulb {bulb.ip}: Constructed pilot: {pilot}")
                            logging.info(f"Bulb {bulb.ip}: Turning on with RGB=({fade_r},{fade_g},{fade_b}), Brightness={brightness}")
                            await bulb.turn_on(pilot)
                            t3=time.time()
                            if t3 - t2 < MIN_FADE_TIME: await asyncio.sleep(t3-t2) 
                t0=time.time()
                pilot = PilotBuilder(rgbww=(step["r"], step["g"], step["b"], 0, 0), brightness=brightness)
                logging.debug(f"Bulb {bulb.ip}: Constructed pilot: {pilot}")
                logging.info(f"Bulb {bulb.ip}: Turning on with RGB=({step['r']}, {step['g']}, {step['b']}), Brightness={brightness}")
                await bulb.turn_on(pilot)
                elapsed = time.time() - t0
                sleep_time = step["hold"] - elapsed
                if sleep_time < 0:
                    sleep_time = 0
                logging.debug(f"Bulb {bulb.ip}: Sleeping for {sleep_time:.2f} sec at step {idx} (hold: {step['hold']}, elapsed: {elapsed:.2f}")
                await asyncio.sleep(sleep_time)
                logging.debug(f"Bulb {bulb.ip}: Completed step {idx}")
        except Exception as e:
            logging.error(f"Error running bulb steps for bulb {bulb.ip} on step {idx}: {e}")
            exit()

def _create_bulb_steps(num_bulbs, colors, step_index, bulb_shift=0):
    step = []
    num_colors = len(colors)
    for bulb_index in range(num_bulbs):
        color_index = (step_index - (bulb_index * bulb_shift)) % num_colors
        print(color_index)
        # Get individual components using the new dictionary structure.
        r = colors[color_index]["r"]
        g = colors[color_index]["g"]
        b = colors[color_index]["b"]
        off_time = colors[color_index].get("off_time", DEFAULT_OFF_TIME)
        # Evaluate the 'hold_time' lambda function if it exists, otherwise get the value directly
        hold_time = colors[color_index].get("hold_time")() if callable(colors[color_index].get("hold_time")) else colors[color_index].get("hold_time", None)
        if hold_time is None:
            hold_time = DEFAULT_HOLD_TIME
        fade_time = colors[color_index].get("fade_time", DEFAULT_FADE_TIME)

        curr_hold_time = off_time if (r == 0 and g == 0 and b == 0) else hold_time
        bulb_step = {
            "r": r,
            "g": g,
            "b": b,
            "cw": 0,
            "ww": 0,
            "hold": curr_hold_time,
            "fade": fade_time
        }
        step.append(bulb_step)
    return step

