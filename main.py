import argparse
import requests
import re
import sys

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

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="command")

info_parser = subparsers.add_parser("info", help="Shows info about a color")
info_parser.add_argument("color", type=str, help="HEX, RGB, HSL, or CMYK of the color to see the info of")
info_parser.add_argument("-f", "--full", help="Shows all avaliable color information, including less common color formats", action="store_true")


palette_parser = subparsers.add_parser("palette", help="Manage color palettes")
palette_subparsers = palette_parser.add_subparsers(dest="action")

create_parser = palette_subparsers.add_parser("create", help="Creates a new color palette")
create_parser.add_argument("name", type=str, help="Palette name")
create_parser.add_argument("colors", type=str, nargs="+", help="HEX, RGB, HSL, or CMYK codes of the colors in the palette")

show_parser = palette_subparsers.add_parser("Show", help="Shows color palettes")
show_parser.add_argument("name", nargs="?", help="Specify a palette to show")

edit_parser = palette_subparsers.add_parser("Edit", help="Edits a color palette")
edit_parser.add_argument("name", "Palette name")

group = edit_parser.add_mutually_exclusive_group(required=True)
group.add_argument("-a", "--add", type=str, nargs="+", help="Adds colors in the HEX, RGB, HSL, or CMYK format to the palette")
group.add_argument("-s", "--set", type=str, nargs="+", help="Sets colors at specific indexes using the format index:color")
group.add_argument("-r", "--remove", type=int, nargs="+", help="Removes colors from the palette at the specified indexes")

delete_parser = palette_subparsers.add_parser("delete", help="Deletes a color palette")
delete_parser.add_argument("name", type="str", help="Palette name")

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

