#!/usr/bin/env python3
"""
Edit SVG element attributes and inline styles in-situ
as long as these changes are not possible in the upstream
dependencies dagviz and snakevision.
Note: this helper script is a temporary solution und will
be removed once more fine-grained styling becomes available.
"""

from pathlib import Path
import xml.etree.ElementTree as ET


def parse_style(style_value: str) -> dict:
    """Convert 'a:b;c:d' style string into a dict."""
    out = {}
    if not style_value:
        return out
    for part in style_value.split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def style_to_string(style_dict: dict) -> str:
    """Convert a style dictionary back into a 'a:b;c:d' string."""
    return ";".join(f"{k}:{v}" for k, v in style_dict.items())


def update_element(el, att):
    """Update an SVG element's attributes and inline style."""
    # direct attributes
    el.set(att[0], att[1])
    # also update inline style="..."
    style = parse_style(el.get("style", ""))
    style[att[0]] = att[1]
    el.set("style", style_to_string(style))


def modify_svg(svg_file: Path, style: str):
    """
    Modify the SVG file in-place based on the specified style.
    """
    SVG_NS = "http://www.w3.org/2000/svg"
    NS = {"svg": SVG_NS}
    ET.register_namespace("", SVG_NS)

    tree = ET.parse(svg_file)
    root = tree.getroot()

    if style == "light":
        updates = {
            "text": {"group": None, "tag": "text", "attribute": ("fill", "darkgrey")}
        }
    elif style == "dark":
        updates = {
            "text": {"group": None, "tag": "text", "attribute": ("fill", "darkgrey")},
            "line": {"group": 2, "tag": "line", "attribute": ("stroke", "black")},
        }
    else:
        raise ValueError(f"Unknown style: {style}")

    for up in updates.values():
        for idx, group in enumerate(root.findall("./svg:g", NS)):
            if up["group"] is not None and idx != int(up["group"]):
                continue
            if up["tag"]:
                elmnt = group.findall(f".//svg:{up['tag']}", NS)
                if elmnt:
                    for e in elmnt:
                        update_element(e, up["attribute"])

    tree.write(svg_file, encoding="utf-8", xml_declaration=True)
