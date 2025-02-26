import random
from wiz_lighting_config import MAX_RGB_VALUE, MIN_RGB_VALUE, DIVERSE_COLORS, BLUE_COLORS
import copy
    
def tr_clr(input_object, math, math_value, keys):
    """
    Transforms the RGB values of a list of colors based on a mathematical operation.

    Args:
        input_object (list): A list of color dictionaries, each with 'r', 'g', 'b' keys.
        math (str): The mathematical operation to perform ('divide', 'multiply', 'add', 'subtract', 'max', 'min', 'random').
        math_value (int): The value to use in the mathematical operation.
        keys (list): The list of color keys ('r', 'g', 'b') to apply the operation to.

    Returns:
        list: The transformed list of color dictionaries.
    """
    for color in input_object:
        for key in keys:
            if math == "divide":
                color[key] = int(color[key]/math_value)
            elif math == "multiply":
                color[key] = int(color[key]*math_value)
            elif math == "add":
                color[key] = int(color[key]+math_value)
            elif math == "subtract":
                color[key] = int(color[key]-math_value)
            elif math == "max":
                color[key] = max(color[key], math_value)
            elif math == "min":
                color[key] = min(color[key], math_value)
            elif math == "random":
                color[key] = random.randint(0, math_value)
            color[key] = max(MIN_RGB_VALUE, min(MAX_RGB_VALUE, int(color[key])))
    return input_object

def colors_less_harsh(colors):
    """
    Reduces the harshness of colors by limiting RGB values.
    """
    return ([{"name": color["name"], "r": min(max(color["r"],50),150), "g": min(max(color["g"],75),200), "b": min(max(color["b"],75),200)} for color in colors])
def define_dynamic_colors():
    global RGB_LESS_HARSH_COLORS
    RGB_LESS_HARSH_COLORS = colors_less_harsh(copy.deepcopy(DIVERSE_COLORS))

    global ICE_STORM_COLORS
    ICE_STORM_COLORS = [
        {"name": "Blue",         "r": 50,   "g": 50,   "b": 255},
        {"name": "LightSkyBlue", "r": 159, "g": 200, "b": 255},
        {"name": "LightCyan",    "r": 175, "g": 238, "b": 238},
        {"name": "White",        "r": 255, "g": 255, "b": 255}
    ]

    global BLUE_ICE_COLORS
    BLUE_ICE_COLORS=tr_clr(tr_clr(tr_clr(copy.deepcopy(ICE_STORM_COLORS), "multiply", 0.5, ["r", "g"]), "multiply", 2, ["b"]), "min", 225, ["b"])

    global BLUER_BRIGHT_RAINBOWY_COLORS
    BLUER_BRIGHT_RAINBOWY_COLORS=tr_clr(tr_clr(tr_clr(copy.deepcopy(DIVERSE_COLORS), "multiply", 0.5, ["r", "g"]), "add", 128, ["b"]), "max", 225, ["b"])

    
    global PENNY_PINK_COLORS
    PENNY_PINK_COLORS = [
        {"name": "Penny Pink",     "r": 250,   "g": 183, "b": 179},
        {"name": "Penny Pink 2",   "r": 190,   "g": 135, "b": 147},
        {"name": "Penny Pink 3",   "r": 140,   "g": 95, "b": 107},
        {"name": "Penny Pink 4",   "r": 105,   "g": 67, "b": 82},
        {"name": "Penny Pink 5",   "r": 70,   "g": 43, "b": 61},
        {"name": "Penny Pink 6",   "r": 43,   "g": 28, "b": 39}
    ]    
    PENNY_PINK_COLORS = tr_clr(tr_clr(tr_clr(copy.deepcopy(PENNY_PINK_COLORS), "divide", 2, ["r", "g","b"]), "add", 100, ["r"]), "max", 225, ["r"])

    global LESS_HARSH_BLUE_COLORS
    LESS_HARSH_BLUE_COLORS=colors_less_harsh(copy.deepcopy(BLUE_COLORS))

    #make them more blue
    for i in range(1,2):
        LESS_HARSH_BLUE_COLORS=tr_clr(tr_clr(tr_clr(tr_clr(LESS_HARSH_BLUE_COLORS,"add",30, ["b"]), "subtract", 300000, ["r","g"]), "add", 50, ["g"]), "add", 20, ["r"])
    
    return
