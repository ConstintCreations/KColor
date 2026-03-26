import argparse
import requests
import re
import os
import sys
import json
import random

PALETTES_FILE = "palettes.json"
GENERATOR_FILE = "generator.json"

def load_palettes():
    if not os.path.exists(PALETTES_FILE):
        return {}
    with open(PALETTES_FILE, "r") as file:
        return json.load(file)

def save_palettes(palettes):
    with open(PALETTES_FILE, "w") as file:
        json.dump(palettes, file, indent=4)

def load_generator():
    if not os.path.exists(GENERATOR_FILE):
        return {
            "settings": {
                "base": "random",
                "scheme": "random",
                "count": 5,
                "name": "New Palette"
            },
            "generation": [

            ]
        }
    with open(GENERATOR_FILE, "r") as file:
        return json.load(file)

def save_generator(generator):
    with open(GENERATOR_FILE, "w") as file:
        json.dump(generator, file, indent=4)


def identifyColor(color_string):
    if re.fullmatch(r"#?[0-9a-f]{6}", color_string):
        return "hex"
    elif re.fullmatch(r"(rgb\()?(\d{1,3}),\s*(\d{1,3}),\s*(\d{1,3})\)?", color_string):
        return "rgb"
    elif re.fullmatch(r"(hsl\()?(\d{1,3}),\s*(\d{1,3})%,\s*(\d{1,3})%\)?", color_string):
        return "hsl"
    elif re.fullmatch(r"(rgb\()?(\d{1,3}),\s*(\d{1,3}),\s*(\d{1,3}),\s*(\d{1,3})\)?", color_string):
        return "cmyk"
    else:
        return None
    
def convertColorsToRGB(color_string, color_format, pair=None):
    colorR = None
    colorG = None
    colorB = None

    if color_format == "rgb":
        if color_string.startswith("rgb(") and color_string.endswith(")"):
            color_string = color_string[4:-1]

        colorR, colorG, colorB = [int(part.strip()) for part in color_string.split(",")]
    elif color_format == "hex":
        if color_string.startswith("#"):
            color_string = color_string[1:]

        colorR, colorG, colorB = int(color_string[0:2], 16), int(color_string[2:4], 16), int(color_string[4:6], 16)
    elif color_format == "hsl":
        if color_string.startswith("hsl(") and color_string.endswith(")"):
            color_string = color_string[4:-1]
        
        h, s, l = [float(part.strip().strip("%")) for part in color_string.split(",")]

        s /= 100
        l /= 100
        c = (1 - abs(2*l - 1)) * s
        x = c * (1 - abs((h/60) %2-1))
        m = l - c/2

        if 0 <= h < 60:
            colorR, colorG, colorB = round((c + m) * 255), round((x + m) * 255), round((0 + m) * 255)
        elif 60 <= h < 120:
            colorR, colorG, colorB = round((x + m) * 255), round((c + m) * 255), round((0 + m) * 255)
        elif 120 <= h < 180:
            colorR, colorG, colorB = round((0 + m) * 255), round((c + m) * 255), round((x + m) * 255)
        elif 180 <= h < 240:
            colorR, colorG, colorB = round((0 + m) * 255), round((x + m) * 255), round((c + m) * 255)
        elif 240 <= h < 300:
            colorR, colorG, colorB = round((x + m) * 255), round((0 + m) * 255), round((c + m) * 255)
        else:
            colorR, colorG, colorB = round((c + m) * 255), round((0 + m) * 255), round((x + m) * 255)

    elif color_format == "cmyk":
        if color_string.startswith("cmyk(") and color_string.endswith(")"):
            color_string = color_string[5:-1]

        c, m, y, k = [int(part.strip())/100 for part in color_string.split(",")]

        colorR, colorG, colorB = round(255 * (1 - c) * (1 - k)), round(255 * (1 - m) * (1 - k)), round(255 * (1 - y) * (1 - k))
    else:
        if pair == None:
            print(f"\nPlease enter valid HEX, RGB, HSL, or CMYK codes\n\nExamples:\nHex : \"#0047ab\" or \"0047ab\"\nRGB : \"rgb(0,71,171)\" or \"0,71,171\"\nHSL : \"hsl(215,100%,34%)\" or \"215,100%,34%\"\nCMYK: \"cmyk(100,58,0,33)\" or \"100,58,0,33\"\n")
        else:
            print(f"\nInvalid format provided for \"{pair}\"\nPlease use the format index:color\n\nPlease enter valid HEX, RGB, HSL, or CMYK codes for the color\n\nExamples:\nHex : \"#0047ab\" or \"0047ab\"\nRGB : \"rgb(0,71,171)\" or \"0,71,171\"\nHSL : \"hsl(215,100%,34%)\" or \"215,100%,34%\"\nCMYK: \"cmyk(100,58,0,33)\" or \"100,58,0,33\"\n")
        sys.exit(1)

    return colorR, colorG, colorB

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="command")

info_parser = subparsers.add_parser("info", help="Shows info about a color")
info_parser.add_argument("color", type=str, help="HEX, RGB, HSL, or CMYK of the color to see the info of")
info_parser.add_argument("-f", "--full", help="Shows all available color information, including less common color formats", action="store_true")


palette_parser = subparsers.add_parser("palette", help="Manage color palettes")
palette_subparsers = palette_parser.add_subparsers(dest="action", required=True)

create_parser = palette_subparsers.add_parser("create", help="Creates a new color palette")
create_parser.add_argument("name", type=str, help="Palette name")
create_parser.add_argument("colors", type=str, nargs="+", help="HEX, RGB, HSL, or CMYK codes of the colors in the palette")

show_parser = palette_subparsers.add_parser("show", help="Shows color palettes")
show_parser.add_argument("name", nargs="?", help="Specify a palette to show")

edit_parser = palette_subparsers.add_parser("edit", help="Edits a color palette")
edit_parser.add_argument("name", type=str, help="Palette name")

group = edit_parser.add_mutually_exclusive_group(required=True)
group.add_argument("-a", "--add", type=str, nargs="+", help="Adds colors in the HEX, RGB, HSL, or CMYK format to the palette")
group.add_argument("-s", "--set", type=str, nargs="+", help="Sets colors at specific indexes using the format index:color")
group.add_argument("-r", "--remove", type=int, nargs="+", help="Removes colors from the palette at the specified indexes")

delete_parser = palette_subparsers.add_parser("delete", help="Deletes a color palette")
delete_parser.add_argument("name", type=str, help="Palette name")

clear_parser = palette_subparsers.add_parser("clear", help="Deletes all color palettes")
clear_parser.add_argument("--confirm", action="store_true", help="Confirms deletion of all color palettes")


generator_parser = subparsers.add_parser("generator", help="Generate color palettes")
generator_subparsers = generator_parser.add_subparsers(dest="action", required=True)

generate_parser = generator_subparsers.add_parser("generate", help="Generate a color palette using the generator's settings")
generate_parser.add_argument("-b", "--base", type=str, help="Overrides the base color for the generator to use for the current generation (random or a HEX, RGB, HSV, or CMYK color code)")
generate_parser.add_argument("-c", "--count", type=int, help="Overrides the number of colors to generate in the color palette for the current generation")
generate_parser.add_argument("-s", "--scheme", type=str, help="Overrides the color scheme for the current generation (random, monochrome, monochrome-dark, monochrome-light, analogic, complement, analogic-complement, triad [count must be 3], or quad [count must be 4])")

settings_parser = generator_subparsers.add_parser("settings", help="Change the generator's settings")
settings_parser.add_argument("-b", "--base", type=str, help="Sets the base color for the generator to use (random or a HEX, RGB, HSV, or CMYK color code)")
settings_parser.add_argument("-c", "--count", type=int, help="Sets the number of colors to generate in the color palette")
settings_parser.add_argument("-s", "--scheme", type=str, help="Sets the color scheme (random, monochrome, monochrome-dark, monochrome-light, analogic, complement, analogic-complement, triad [count must be 3], or quad [count must be 4])")
settings_parser.add_argument("-n", "--name", type=str, help="Changes the active color palette's name in the generator")

generator_show_parser = generator_subparsers.add_parser("show", help="Shows the generator's last generation")

lock_parser = generator_subparsers.add_parser("lock", help="Locks the colors at the given indexes")
lock_parser.add_argument("indexes", type=int, nargs="+", help="Indexes to lock the colors at")
unlock_parser = generator_subparsers.add_parser("unlock", help="Unlocks the colors at the given indexes")
unlock_parser.add_argument("indexes", type=int, nargs="+", help="Indexes to unlock the colors at")

save_parser = generator_subparsers.add_parser("save", help="Saves the last generated color palette")
save_parser.add_argument("name", type=str, nargs="?", help="Uses this name for the saved color palette")

load_parser = generator_subparsers.add_parser("load", help="Loads the specified color palette to the generator")
load_parser.add_argument("name", type=str, help="Palette name")

args = parser.parse_args()

if args.command == "info":
    color_string = args.color.strip().lower()

    color_format = identifyColor(color_string)

    if not(color_format):
        print(f"\nPlease enter a valid HEX, RGB, HSL, or CMYK code\n\nExamples:\nHex : \"#0047ab\" or \"0047ab\"\nRGB : \"rgb(0,71,171)\" or \"0,71,171\"\nHSL : \"hsl(215,100%,34%)\" or \"215,100%,34%\"\nCMYK: \"cmyk(100,58,0,33)\" or \"100,58,0,33\"\n")
        sys.exit(1)

    req = requests.get(f"https://www.thecolorapi.com/id?{color_format}={color_string}")
    if req.status_code != 200:
        print("\nError returning color information\nPlease check that you entered a valid format\n\nExamples:\nHex : \"#0047ab\" or \"0047ab\"\nRGB : \"rgb(0,71,171)\" or \"0,71,171\"\nHSL : \"hsl(215,100%,34%)\" or \"215,100%,34%\"\nCMYK: \"cmyk(100,58,0,33)\" or \"100,58,0,33\"\n")
        sys.exit(1)
    parsed = req.json()
    if args.full:
        print(f"\n\033[38;2;{parsed["rgb"]["r"]};{parsed["rgb"]["g"]};{parsed["rgb"]["b"]}m \u2588\u2588 \033[0m {parsed["name"]["value"]}\n")

        print(f"Name:\n  Color Name: {parsed["name"]["value"]}\n  Exact Match: {"Yes" if parsed["name"]["exact_match_name"] == True else f"No\n  Closest Exact Match Hex: {parsed["name"]["closest_named_hex"]}\n  Distance from Exact Match: {parsed["name"]["distance"]}"}\n")

        print(f"HEX : {parsed["hex"]["value"].lower()}")
        print(f"RGB : {parsed["rgb"]["value"]}")
        print(f"HSL : {parsed["hsl"]["value"]}")
        print(f"HSV : {parsed["hsv"]["value"]}")
        print(f"CMYK: {parsed["cmyk"]["value"]}")
        print(f"XYZ : {parsed["XYZ"]["value"]}")
        print(f"\nBest Text Color: {"\033[38;2;255;255;255m\u2588\u2588\033[0m White" if parsed["contrast"]["value"] == "#ffffff" else "\033[38;2;0;0;0m\u2588\u2588\033[0m Black"}\n")
    else:
        print(f"\n\033[38;2;{parsed["rgb"]["r"]};{parsed["rgb"]["g"]};{parsed["rgb"]["b"]}m \u2588\u2588 \033[0m {parsed["name"]["value"]}\n")
        print(f"HEX: {parsed["hex"]["value"].lower()}")
        print(f"RGB: {parsed["rgb"]["value"]}")
        print(f"HSL: {parsed["hsl"]["value"]}")
        print(f"\nBest Text Color: {"\033[38;2;255;255;255m\u2588\u2588\033[0m White" if parsed["contrast"]["value"] == "#ffffff" else "\033[38;2;0;0;0m\u2588\u2588\033[0m Black"}\n")

elif args.command == "palette":
    if args.action == "create":
        palettes = load_palettes()

        if args.name in palettes:
            print(f"\nColor palette with name \"{args.name}\" already exists\nIf you wish to edit that palette, use \"palette edit {args.name}\"\n")
            sys.exit(1)

        color_list = []
        for color_string in args.colors:
            color = color_string.strip().lower()
            color_format = identifyColor(color)

            colorR, colorG, colorB = convertColorsToRGB(color, color_format)

            colorHEX = f"#{colorR:02X}{colorG:02X}{colorB:02X}"

            color_list.append({"colorBox": f"\033[38;2;{colorR};{colorG};{colorB}m\u2588\u2588\033[0m", "hex": colorHEX.lower()})
        
        palettes[args.name] = color_list
        save_palettes(palettes)

        print(f"\nPalette Created:\n\n{args.name}:")
        for i, color in enumerate(palettes[args.name]):
            print(f"[{i+1}] {color["colorBox"]} {color["hex"]}")
        print("")

    elif args.action == "show":
        palettes = load_palettes()

        if args.name:
            if not(args.name in palettes):
                print(f"\nNo color palette with the name \"{args.name}\" was found\n")
                sys.exit(1)
            print(f"\n{args.name}:")
            for i, color in enumerate(palettes[args.name]):
                print(f"[{i+1}] {color["colorBox"]} {color["hex"]}")
            print("")
            sys.exit(0)

        if len(palettes) == 0:
            print("\nNo color palettes were found\nCreate one with \"palette create\"\n")
            sys.exit(1)
        
        print("\nAll Palettes:")

        for palette in palettes:
            print(f"\n{palette}:")
            for i, color in enumerate(palettes[palette]):
                print(f"[{i+1}] {color["colorBox"]} {color["hex"]}")
        print("")
        
    elif args.action == "edit":
        palettes = load_palettes()
        if not(args.name in palettes):
            print(f"\nNo color palette with the name \"{args.name}\" was found\n")
            sys.exit(1)

        if args.add:
            
            color_list = []
            for color_string in args.add:
                color = color_string.strip().lower()
                color_format = identifyColor(color)

                colorR, colorG, colorB = convertColorsToRGB(color, color_format)

                colorHEX = f"#{colorR:02X}{colorG:02X}{colorB:02X}"

                color_list.append({"colorBox": f"\033[38;2;{colorR};{colorG};{colorB}m\u2588\u2588\033[0m", "hex": colorHEX.lower()})
            
            palettes[args.name] = palettes[args.name] + color_list
            save_palettes(palettes)

            print(f"\nColors added")

        elif args.remove:
            new_palette = []

            removed_indexes = []

            for index, color in enumerate(palettes[args.name]):
                if not((index+1) in args.remove):
                    new_palette.append(color)
                else:
                    removed_indexes.append(index+1)

            if len(new_palette) == 0:
                print(f"\nEmpty color palette with the name \"{args.name}\" was deleted\n")
                del palettes[args.name]
                save_palettes(palettes)
                sys.exit(0)

            palettes[args.name] = new_palette
            save_palettes(palettes)


            if len(removed_indexes) == 0:
                print(f"\nNo colors were found at the provided indexes\n")
                sys.exit(1)

            removed_indexes_string = ""
            removed_indexes = [str(index) for index in removed_indexes]
            if len(removed_indexes) == 1:
                removed_indexes_string = removed_indexes[0]
            elif len(removed_indexes) == 2:
                removed_indexes_string = removed_indexes[0] + " and " + removed_indexes[1]
            elif len(removed_indexes) > 2:
                removed_indexes_string = ", ".join(removed_indexes[:-1]) + ", and " + removed_indexes[-1]

            print(f"\n{"Color" if len(removed_indexes) == 1 else "Colors"} removed at {"index" if len(removed_indexes) == 1 else "indexes"} {removed_indexes_string}")



        elif args.set:
            changes = []
            for pair in args.set:
                try:
                    index_string, color_string = pair.split(":")
                    index = int(index_string)

                    color = color_string.strip().lower()
                    color_format = identifyColor(color)

                    colorR, colorG, colorB = convertColorsToRGB(color, color_format, pair)

                    colorHEX = f"#{colorR:02X}{colorG:02X}{colorB:02X}"

                    changes.append({"index": f"{index}", "colorBox": f"\033[38;2;{colorR};{colorG};{colorB}m\u2588\u2588\033[0m", "hex": colorHEX.lower()})
                except ValueError:
                    print(f"\nInvalid format provided for \"{pair}\"\nPlease use the format index:color\n")
                    sys.exit(1)
            
            edited_indexes = []

            for change in changes:
                for index, _ in enumerate(palettes[args.name]):
                    if int(change["index"])-1 == index:
                        edited_indexes.append(change["index"])
                        palettes[args.name][index] = {"colorBox": change["colorBox"], "hex": change["hex"]}

            save_palettes(palettes)

            if len(edited_indexes) == 0:
                print(f"\nNo colors were found at the provided indexes\n")
                sys.exit(1)

            edited_indexes_string = ""
            edited_indexes = [str(index) for index in edited_indexes]
            if len(edited_indexes) == 1:
                edited_indexes_string = edited_indexes[0]
            elif len(edited_indexes) == 2:
                edited_indexes_string = edited_indexes[0] + " and " + edited_indexes[1]
            elif len(edited_indexes) > 2:
                edited_indexes_string = ", ".join(edited_indexes[:-1]) + ", and " + edited_indexes[-1]

            print(f"\n{"Color" if len(edited_indexes) == 1 else "Colors"} edited at {"index" if len(edited_indexes) == 1 else "indexes"} {edited_indexes_string}")
                

        print(f"\nNew Color Palette:\n\n{args.name}:")
        for i, color in enumerate(palettes[args.name]):
            print(f"[{i+1}] {color["colorBox"]} {color["hex"]}")
        print("")
    elif args.action == "delete":
        palettes = load_palettes()
        if args.name in palettes:
            del palettes[args.name]
            save_palettes(palettes)
            print(f"Color palette with the name \"{args.name}\" was successfully deleted\n")
        else:
            print(f"\nNo color palette with the name \"{args.name}\" was found\n")
            sys.exit(1)
    elif args.action == "clear":
        if args.confirm:
            save_palettes({})
            print("\nAll color palettes have been deleted\n")
        else:
            print("\n\U000026A0 Warning: This will delete all saved color palettes \U000026A0\n\n     To proceed with the deletion, use --confirm\n")
elif args.command == "generator":
    if args.action == "show":
        generator = load_generator()
        settings = generator["settings"]
        generation = generator["generation"]

        if len(generation) == 0:
            print("\n   No generated palette available\nUse \"generator generate\" to make one\n")
            sys.exit(1)
        
        print(f"\nLast Palette Generated:\n\n{settings["name"]}:")

        for i, color in enumerate(generation):
            print(f"[{i+1}] [{"L" if color["locked"] == True else " "}] {color["colorBox"]} {color["hex"]}")
        print("")

    elif args.action == "settings":
        generator = load_generator()
        settings = generator["settings"]

        if args.base:
            color_string = args.base.strip().lower()

            if color_string == "random":
                settings["base"] = "random"
            else:

                color_format = identifyColor(color_string)

                colorR, colorG, colorB = convertColorsToRGB(color_string, color_format)

                colorHEX = f"#{colorR:02X}{colorG:02X}{colorB:02X}" 

                settings["base"] = colorHEX.lower()
        if args.scheme:
            valid_schemes = ["random", "monochrome", "monochrome-dark", "monochrome-light", "analogic", "complement", "analogic-complement", "triad", "quad"]
            scheme = args.scheme.strip().lower()

            if not(scheme in valid_schemes):
                print(f"\n        Invalid scheme provided\nPlease use one of the following schemes: \n\n{"\n".join(valid_schemes)}")
            else:
                settings["scheme"] = scheme
                if scheme == "triad":
                    settings["count"] = 3
                elif scheme == "quad":
                    settings["count"] = 4
        if args.count:
            count = int(args.count)
            if (settings["scheme"] == "triad" and count != 3) or (settings["scheme"] == "quad" and count != 4):
                print(f"\nCannot change count from {settings["count"]} while the {settings["scheme"].capitalize()} scheme is selected")
            elif count < 2 or count > 1000:
                print(f"\n     Count was not changed\nCount must be between 2 and 1000")
            else:
                settings["count"] = count
        if args.name:
            settings["name"] = args.name
        
        generator["settings"] = settings
        save_generator(generator)

        print(f"\nGenerator Settings:\n\nBase  : {"Random" if settings["base"] == "random" else settings["base"]}\nScheme: {"Random" if settings["scheme"] == "random" else f"{" ".join(word.capitalize() for word in settings["scheme"].replace("-", " ").split())}"}\nCount : {settings["count"]}\nName  : {settings["name"]}\n")
    elif args.action == "save":
        palettes = load_palettes()
        generator = load_generator()
        settings = generator["settings"]
        generation = generator["generation"].copy()

        if len(generation) == 0:
            print("\n   No generated palette available\nUse \"generator generate\" to make one\n")
            sys.exit(1)

        if args.name:
            settings["name"] = args.name
            generator["settings"] = settings
            save_generator(generator)

        for i, _ in enumerate(generation):
            del generation[i]["locked"]

        palettes[settings["name"]] = generation

        save_palettes(palettes)

        print(f"\nGenerated Palette Saved:\n\n{settings["name"]}:")
        for i, color in enumerate(palettes[settings["name"]]):
            print(f"[{i+1}] {color["colorBox"]} {color["hex"]}")
        print("")

    elif args.action == "load":
        palettes = load_palettes()
        generator = load_generator()
        settings = generator["settings"]
        generation = generator["generation"]

        new_colors = []

        if len(palettes) == 0:
            print("\nNo color palettes were found\nCreate one with \"palette create\"\n")
            sys.exit(1)

        if not(args.name in palettes):
            print(f"\nNo color palette with the name \"{args.name}\" was found\n")
            sys.exit(1)
        
        settings["name"] = args.name
        for color in palettes[args.name]:
            new_colors.append({"colorBox": color["colorBox"], "hex": color["hex"], "locked": False})
        
        generator["settings"] = settings
        generator["generation"] = new_colors
        save_generator(generator)

        print(f"\nPalette Loaded:\n\n{settings["name"]}:")

        for i, color in enumerate(new_colors):
            print(f"[{i+1}] [{"L" if color["locked"] == True else " "}] {color["colorBox"]} {color["hex"]}")
        print("")

    elif args.action == "generate":
        generator = load_generator()
        override_settings = generator["settings"].copy()
        generation = generator["generation"]

        valid_schemes = ["random", "monochrome", "monochrome-dark", "monochrome-light", "analogic", "complement", "analogic-complement", "triad", "quad"]

        if args.base:
            color_string = args.base.strip().lower()

            if color_string == "random":
                override_settings["base"] = "random"
            else:

                color_format = identifyColor(color_string)

                colorR, colorG, colorB = convertColorsToRGB(color_string, color_format)

                colorHEX = f"#{colorR:02X}{colorG:02X}{colorB:02X}" 

                override_settings["base"] = colorHEX.lower()
        if args.scheme:
            scheme = args.scheme.strip().lower()

            if not(scheme in valid_schemes):
                print(f"\n        Invalid scheme provided\nPlease use one of the following schemes: \n\n{"\n".join(valid_schemes)}\n")
                sys.exit(1)
            else:
                override_settings["scheme"] = scheme
                if scheme == "triad":
                    override_settings["count"] = 3
                elif scheme == "quad":
                    override_settings["count"] = 4
        if args.count:
            count = int(args.count)
            if (override_settings["scheme"] == "triad" and count != 3) or (override_settings["scheme"] == "quad" and count != 4):
                print(f"\nCannot change count from {override_settings["count"]} while the {override_settings["scheme"].capitalize()} scheme is selected\n")
                sys.exit(1)
            elif count < 2 or count > 1000:
                print(f"\n     Count was not changed\nCount must be between 2 and 1000\n")
                sys.exit(1)
            else:
                override_settings["count"] = count

        if override_settings["base"] == "random":
            override_settings["base"] = "".join(f"{random.randint(0,15):X}" for _ in range(6))
        else:
            override_settings["base"] = override_settings["base"][1:] if override_settings["base"].startswith("#") else override_settings["base"]

        if override_settings["scheme"] == "random":
            override_settings["scheme"] = random.choice(valid_schemes[1:-2])

        req = requests.get(f"https://www.thecolorapi.com/scheme?hex={override_settings["base"]}&mode={override_settings["scheme"]}&count={override_settings["count"]}")
        if req.status_code != 200:
            print("\nUnexpected error generating color palette\n")
            sys.exit(1)
        parsed = req.json()

        colors = parsed["colors"]

        new_colors = []

        for i, color in enumerate(colors):
            if i < len(generation) and generation[i].get("locked"):
                new_colors.append(generation[i])
            else:
                new_colors.append({"colorBox": f"\033[38;2;{color["rgb"]["r"]};{color["rgb"]["g"]};{color["rgb"]["b"]}m\u2588\u2588\033[0m", "hex": color["hex"]["value"].lower(), "locked": False})

        generator["generation"] = new_colors
        save_generator(generator)

        print(f"\nPalette Generated:\n\n{override_settings["name"]}:")

        for i, color in enumerate(new_colors):
            print(f"[{i+1}] [{"L" if color["locked"] == True else " "}] {color["colorBox"]} {color["hex"]}")
        print("")

    elif args.action == "lock":
        generator = load_generator()
        settings = generator["settings"]
        generation = generator["generation"]

        if len(generation) == 0:
            print("\n   No generated palette available\nUse \"generator generate\" to make one\n")
            sys.exit(1)

        indexes = args.indexes
        locked_indexes = []

        for index in indexes:
            for jindex, _ in enumerate(generation):
                if index-1 == jindex:
                    locked_indexes.append(index)
                    generation[jindex]["locked"] = True
        
        generator["generation"] = generation
        save_generator(generator)

        if len(locked_indexes) == 0:
                print(f"\nNo colors were found at the provided indexes\n")
                sys.exit(1)

        locked_indexes_string = ""
        locked_indexes = [str(index) for index in locked_indexes]
        if len(locked_indexes) == 1:
            locked_indexes_string = locked_indexes[0]
        elif len(locked_indexes) == 2:
            locked_indexes_string = locked_indexes[0] + " and " + locked_indexes[1]
        elif len(locked_indexes) > 2:
            locked_indexes_string = ", ".join(locked_indexes[:-1]) + ", and " + locked_indexes[-1]

        print(f"\n{"Color" if len(locked_indexes) == 1 else "Colors"} locked at {"index" if len(locked_indexes) == 1 else "indexes"} {locked_indexes_string}")
        
        print(f"\nLast Palette Generated:\n\n{settings["name"]}:")

        for i, color in enumerate(generation):
            print(f"[{i+1}] [{"L" if color["locked"] == True else " "}] {color["colorBox"]} {color["hex"]}")
        print("")
    elif args.action == "unlock":
        generator = load_generator()
        settings = generator["settings"]
        generation = generator["generation"]

        if len(generation) == 0:
            print("\n   No generated palette available\nUse \"generator generate\" to make one\n")
            sys.exit(1)

        indexes = args.indexes
        unlocked_indexes = []

        for index in indexes:
            for jindex, _ in enumerate(generation):
                if index-1 == jindex:
                    unlocked_indexes.append(index)
                    generation[jindex]["locked"] = False
        
        generator["generation"] = generation
        save_generator(generator)

        if len(unlocked_indexes) == 0:
                print(f"\nNo colors were found at the provided indexes\n")
                sys.exit(1)

        unlocked_indexes_string = ""
        unlocked_indexes = [str(index) for index in unlocked_indexes]
        if len(unlocked_indexes) == 1:
            unlocked_indexes_string = unlocked_indexes[0]
        elif len(unlocked_indexes) == 2:
            unlocked_indexes_string = unlocked_indexes[0] + " and " + unlocked_indexes[1]
        elif len(unlocked_indexes) > 2:
            unlocked_indexes_string = ", ".join(unlocked_indexes[:-1]) + ", and " + unlocked_indexes[-1]

        print(f"\n{"Color" if len(unlocked_indexes) == 1 else "Colors"} unlocked at {"index" if len(unlocked_indexes) == 1 else "indexes"} {unlocked_indexes_string}")
        
        print(f"\nLast Palette Generated:\n\n{settings["name"]}:")

        for i, color in enumerate(generation):
            print(f"[{i+1}] [{"L" if color["locked"] == True else " "}] {color["colorBox"]} {color["hex"]}")
        print("")