"""Terminal output in the anarchygames.org palette."""

import os
import re
import sys
import textwrap

ORANGE = (232, 93, 4)
AMBER = (250, 163, 7)
GOLD = (255, 208, 0)
CYAN = (0, 212, 255)
PINK = (255, 45, 123)
GREEN = (63, 185, 80)
TEXT = (200, 204, 212)
MUTED = (106, 112, 128)
DIM = (58, 64, 80)

COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
WIDTH = 74


def c(rgb, s, bold=False):
    if not COLOR:
        return s
    b = "1;" if bold else ""
    return f"\033[{b}38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{s}\033[0m"


def code(s):
    """Render `backticked` spans as commands."""
    return re.sub(r"`([^`]+)`", lambda m: c(AMBER, m.group(1)), s)


def para(text, indent=2):
    out = []
    for block in text.strip("\n").split("\n\n"):
        lines = block.split("\n")
        # Lines indented in the source (examples, trees) are kept as written.
        if any(l.startswith("    ") for l in lines):
            out.append("\n".join(" " * indent + code(l) for l in lines))
        else:
            wrapped = textwrap.fill(" ".join(l.strip() for l in lines), WIDTH - indent)
            out.append(textwrap.indent(code(wrapped), " " * indent))
    return "\n\n".join(out)


def streak(n, total):
    n = min(n, total)
    return c(ORANGE, "●" * n) + c(DIM, "○" * (total - n))


def bar(left, right=""):
    pad = WIDTH - len(left) - len(right) - 3
    return c(ORANGE, "▌ ") + c(TEXT, left, bold=True) + " " * max(pad, 1) + c(MUTED, right)


def ok(s):
    return c(GREEN, "✔ ", bold=True) + s


def bad(s):
    return c(PINK, "✘ ", bold=True) + s


def muted(s):
    return c(MUTED, s)
