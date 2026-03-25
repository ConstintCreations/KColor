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

#print(" [\U0001F512]      [\U0001F512]")
#print(" \033[38;2;171;192;222m \u2588\u2588 \033[0m \033[38;2;171;192;222m \u2588\u2588 \033[0m \033[38;2;171;192;222m \u2588\u2588 \033[0m")