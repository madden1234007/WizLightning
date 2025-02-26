import math
import asyncio
import time
import random
import logging
import copy
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from pywizlight import wizlight, PilotBuilder
from WizLightingDefs import _create_steps, _run_bulbs
from wiz_lighting_config import make_default_config_dict
from wiz_extended_colors import define_dynamic_colors
from WizLightingInit import init_devices, after_init_devices_2

# --- Global Variables ---
lamp_groups = {}
running = False
loop = asyncio.get_event_loop()
lamp_buttons = {}
active_tasks = set()
initial_color_textboxes = {}
final_color_textboxes = {}
lamp_group_frames = {}
step_textboxes = {}
start_button = None

class LampGroup:
    def __init__(self, name, ips, colors=None, bulb_shift=0, is_enabled=False):
        config = make_default_config_dict(name, ips)
        for key, value in config.items():
            setattr(self, key, value)
        self.initial_colors = copy.deepcopy(colors) if colors is not None else []
        self.bulb_shift = bulb_shift
        self.is_enabled = is_enabled
        self.task = None
        self.name = name
        self.ips = ips
        self.colors = []  # Create the proper list
        self.apply_new_colors(colors)  # Populate self.colors
        self.steps = _create_steps(len(ips), self.colors, bulb_shift)

    def __str__(self):
        return f"<LampGroup: {self.name}, enabled:{self.is_enabled}>"

    def apply_new_colors(self, new_colors):
        """Applies new colors to the group, preserving additional parameters."""
        if new_colors is None:
            self.colors = []
            self.steps = _create_steps(len(self.ips), self.colors, self.bulb_shift)
            return

        # Create a list to hold the new colors with preserved parameters
        new_colors_with_params = []
        
        # Extract all keys from initial colors to preserve extra params.
        keys_to_preserve = set()
        for color in self.initial_colors:
            keys_to_preserve.update(color.keys())
        

        for i, color in enumerate(new_colors):
            # Create a new color dictionary with r, g, b values
            new_color = {'r': color.get('r', 0), 'g': color.get('g', 0), 'b': color.get('b', 0)}
            
            # Add any other keys from the original color
            for key in keys_to_preserve:
              if key != 'r' and key != 'g' and key != 'b' and key in self.initial_colors[i]:
                  new_color[key] = self.initial_colors[i][key]
            new_colors_with_params.append(new_color)
        
        self.colors = new_colors_with_params
        self.steps = _create_steps(len(self.ips), self.colors, self.bulb_shift)


# --- Helper Function to Format Color Data ---
def format_color_data(colors):
    """Formats color data for display in the text boxes with line breaks."""
    return str(colors)


# --- Helper function to format step data for display in the text boxes with indentation and line breaks ---
def format_step_data(steps):
    """Formats step data for display in the text boxes with indentation and line breaks."""
    return str(steps)


# --- Main Lamp Control Logic ---
async def lamp_control_logic():
    global running, lamp_groups, active_tasks
    while running:
        for group_name, group_config in lamp_groups.items():
            if group_config.is_enabled:
                if group_config.task is None:
                    logging.info(f"Creating task for {group_config}")
                    group_config.task = asyncio.create_task(
                        _run_bulbs(group_config.__dict__, group_config.steps, random_color_check=0, async_groups="steps")
                    )
                    active_tasks.add(group_config.task)
                    logging.info(f"Task {group_config.task} created for {group_config}")
            else:
                if group_config.task is not None:
                    logging.info(f"Cancelling task {group_config.task} for {group_config}")
                    group_config.task.cancel()
                    active_tasks.discard(group_config.task)
                    try:
                        await asyncio.wait_for(group_config.task, timeout=0.5)
                    except asyncio.TimeoutError:
                        logging.warning(f"Task {group_config.task} for {group_config} did not cancel in time.")
                    except asyncio.CancelledError:
                        logging.info(f"Task {group_config.task} for {group_config} cancelled successfully.")
                    group_config.task = None
                    logging.info(f"Task {group_config.task} for {group_config} cancelled and cleared.")

        # Remove completed tasks
        for task in active_tasks.copy():
            if task.done():
                logging.info(f"Task {task} completed.")
                active_tasks.remove(task)

        await asyncio.sleep(1)


# --- GUI Functions ---
def start_lamp_control():
    global running
    if not running:
        running = True
        start_button.config(text="Deactivate Lighting")
        logging.info("Activate Lighting button pressed. Starting main loop.")
        lamp_thread = threading.Thread(target=asyncio_run_lamp_control, daemon=True)
        lamp_thread.start()
    else:
        stop_lamp_control()


def stop_lamp_control():
    global running, loop
    if running:
        running = False
        start_button.config(text="Activate Lighting")
        logging.info("Deactivate Lighting button pressed. Stopping main loop and all tasks.")
        for task in active_tasks:
            task.cancel()
        active_tasks.clear()
        loop.call_soon_threadsafe(loop.stop)
        for group in lamp_groups.values():
            if group.task is not None:
                group.task.cancel()
            group.task = None
        update_lamp_gui()


def toggle_group_control(group_name):
    global lamp_groups, running
    group = lamp_groups[group_name]
    group.is_enabled = not group.is_enabled
    logging.info(f"Toggling group {group_name} to {'enabled' if group.is_enabled else 'disabled'}")
    update_lamp_gui()


def asyncio_run_lamp_control():
    global loop
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(lamp_control_logic())
    except RuntimeError as e:
        if "loop is closed" not in str(e):
            logging.exception("Unexpected error in lamp_control_logic:")
    finally:
        pass


def update_lamp_gui():
    """Updates the lamp start/stop buttons in the GUI."""
    for group_name, button in lamp_buttons.items():
        for lamp_group in lamp_groups.values():
            if lamp_group.name == group_name:
                if lamp_group.is_enabled:
                    button.config(text=f"Disable {group_name}")
                else:
                    button.config(text=f"Enable {group_name}")


def update_steps(group_name):
    """Updates the steps for the selected group."""
    global step_textboxes
    try:
        group = lamp_groups[group_name]
        new_steps_str = step_textboxes[group_name].get("1.0", tk.END).strip()
        new_steps = eval(new_steps_str)
        group.steps = new_steps
    except (SyntaxError, NameError, ValueError) as e:
        logging.error(f"Invalid step format for {group_name}: {e}. Please use a list of dictionaries.")
        messagebox.showerror("Error", f"Invalid step format for {group_name}: {e}. Please use a list of dictionaries.")


def load_default_steps(group_name):
    global step_textboxes, final_color_textboxes, initial_color_textboxes
    group = lamp_groups[group_name]
    group.steps = _create_steps(len(group.ips), group.colors, group.bulb_shift)
    step_textboxes[group_name].delete("1.0", tk.END)
    step_textboxes[group_name].insert(tk.END, str(group.steps))
    final_color_textboxes[group_name].delete("1.0", tk.END)
    final_color_textboxes[group_name].insert(tk.END, str(group.colors))
    initial_color_textboxes[group_name].delete("1.0", tk.END)
    initial_color_textboxes[group_name].insert(tk.END, str(group.initial_colors))


from tkinter import messagebox

def apply_colors(group_name):
    """Applies new colors to the specified group."""
    global initial_color_textboxes, final_color_textboxes, step_textboxes
    try:
        group = lamp_groups[group_name]
        new_initial_colors_str = initial_color_textboxes[group_name].get("1.0", tk.END).strip()
        new_final_colors_str = final_color_textboxes[group_name].get("1.0", tk.END).strip()
        
        #Improved validation of the data:
        try:
            new_initial_colors = eval(new_initial_colors_str)
            new_final_colors = eval(new_final_colors_str)
            group.apply_new_colors(new_final_colors)
            group.initial_colors = new_initial_colors
            update_steps(group_name)
        except (SyntaxError, NameError, ValueError) as e:
            logging.error(f"Invalid color format for {group_name}: {e}")
            messagebox.showerror("Error", f"Invalid color format for {group_name}: {e}")

    except Exception as e:
        logging.exception(f"An unexpected error occurred while applying colors to {group_name}: {e}")
        messagebox.showerror("Error", f"An unexpected error occurred while applying colors to {group_name}: {e}")

# --- GUI Setup ---
root = tk.Tk()
root.title("Lamp Controller")

# Main Frame for Groups (using grid layout)
main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# --- Main Execution ---
async def gui_main():
    global lamp_groups, lamp_group_frames, step_textboxes, lamp_buttons, running, initial_color_textboxes, final_color_textboxes, start_button
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
    lamp_configs = init_devices()
    define_dynamic_colors()
    lamp_configs = after_init_devices_2(lamp_configs)

    # Configure row and column weights for resizing
    main_frame.rowconfigure(0, weight=0)  # Row for button
    main_frame.rowconfigure(1, weight=1)  # Row for groups

    #place the button now that we know how many groups to expect.
    start_button = ttk.Button(main_frame, text="Activate Lighting", command=start_lamp_control)
    start_button.grid(row=0, column=0, columnspan=len(lamp_configs), pady=20) # now uses the length of the config dict to get group numbers

    for i in range(len(lamp_configs)):
        main_frame.columnconfigure(i, weight=1)  # Distribute columns

    column_num = 0
    for name, config in lamp_configs.items():
        lamp_groups[name] = LampGroup(name, config["ips"], config["colors"], config["bulb_shift"], is_enabled=True)

        # Create a frame for each lamp group
        group_frame = ttk.LabelFrame(main_frame, text=name)
        group_frame.grid(row=1, column=column_num, padx=10, pady=10, sticky="nsew")
        lamp_group_frames[name] = group_frame

        # Configure row weights for group frame
        for x in range(10):
            group_frame.rowconfigure(x, weight=0)
        group_frame.rowconfigure(5, weight=1) #let steps resize

        group_frame.columnconfigure(0, weight=1)

        # Initial Color Box
        initial_color_label = ttk.Label(group_frame, text="Initial Colors:")
        initial_color_label.grid(row=0, column=0, pady=2, sticky="ew")
        initial_color_textbox = scrolledtext.ScrolledText(group_frame, height=2, wrap=tk.WORD)
        initial_color_textbox.grid(row=1, column=0, padx=5, pady=2, sticky="nsew")
        initial_color_textboxes[name] = initial_color_textbox

        # Final Color Box
        final_color_label = ttk.Label(group_frame, text="Final Colors:")
        final_color_label.grid(row=2, column=0, pady=2, sticky="ew")
        final_color_textbox = scrolledtext.ScrolledText(group_frame, height=2, wrap=tk.WORD)
        final_color_textbox.grid(row=3, column=0, padx=5, pady=2, sticky="nsew")
        final_color_textboxes[name] = final_color_textbox

        # Steps Box (with scrollbar)
        step_label = ttk.Label(group_frame, text="Steps:")
        step_label.grid(row=4, column=0, pady=2, sticky="ew")
        step_textbox = scrolledtext.ScrolledText(group_frame, height=10, wrap=tk.NONE) # changed wrap to tk.NONE
        step_textbox.grid(row=5, column=0, padx=5, pady=5, sticky="nsew")
        step_textboxes[name] = step_textbox

        # Add a button to update steps
        update_button = ttk.Button(group_frame, text="Update Steps", command=lambda name=name: update_steps(name))
        update_button.grid(row=6, column=0, pady=5, sticky="ew")

        # Add a button to load default steps
        default_button = ttk.Button(group_frame, text="Load Default Steps", command=lambda name=name: load_default_steps(name))
        default_button.grid(row=7, column=0, pady=5, sticky="ew")

        # Add a button to update colors
        apply_button = ttk.Button(group_frame, text="Apply Changes", command=lambda name=name: apply_colors(name))
        apply_button.grid(row=8, column=0, pady=5, sticky="ew")

        # Start/Stop button per group
        start_stop_button = ttk.Button(group_frame, text=f"Disable {name}", command=lambda name=name: toggle_group_control(name))
        start_stop_button.grid(row=9, column=0, pady=5, sticky="ew")
        lamp_buttons[name] = start_stop_button

        # Load initial steps into the textbox, as well as the color boxes.
        load_default_steps(name)

        column_num += 1 #iterate the column

    start_lamp_control()
    root.mainloop()

if __name__ == "__main__":
    asyncio.run(gui_main())
