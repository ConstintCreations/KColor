import argparse
import requests
import re
import os
import sys
import json

PALETTES_FILE = "palettes.json"

def load_palettes():
    if not os.path.exists(PALETTES_FILE):
        return {}
    with open(PALETTES_FILE, "r") as file:
        return json.load(file)

def save_palettes(palettes):
    with open(PALETTES_FILE, "w") as file:
        json.dump(palettes, file, indent=4)


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

        colorR, colorB, colorG = round(255 * (1 - c) * (1 - k)), round(255 * (1 - m) * (1 - k)), round(255 * (1 - y) * (1 - k))
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
info_parser.add_argument("-f", "--full", help="Shows all avaliable color information, including less common color formats", action="store_true")


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