"""Correct shell solutions for every exercise. Shared by the tests and the smoke run."""

from pathlib import Path

OUT = object()  # "use the script's output as the answer"


def q(p):
    return "'" + str(p).replace("'", "'\\''") + "'"


SOLUTIONS = {
    "help.flag": lambda st: (None, st["answers"][0]),
    "help.man": lambda st: (None, st["answers"][-1]),
    "help.apropos": lambda st: (None, st["cmd"]),
    "help.synopsis": lambda st: (None, " ".join(st["answers"])),
    "help.tldr": lambda st: (f"cd {q(st['dl'])} && tar xf {q(st['name'])}", None),
    "nav.goto": lambda st: (f"cd {q(st['dest'])}", None),
    "nav.relative": lambda st: (f"cd {'../' * st['up']}{st['down']}", None),
    "nav.fullpath": lambda st: (f'echo "$(pwd)/{Path(st["file"]).name}"', OUT),
    "nav.hidden": lambda st: (f"ls -A {q(st['dir'])} | grep '^\\.'", OUT),
    "nav.whichdir": lambda st: (f"ls -F {q(st['dir'])} | grep '/$' | tr -d /", OUT),
    "files.tree": lambda st: ("mkdir -p " + " ".join(q(Path(st["root"]) / w) for w in st["wanted"]), None),
    "files.sort": lambda st: (
        f"cd {q(st['dl'])} && for f in *.jpg *.png; do [ -e \"$f\" ] && mv \"$f\" {q(st['pics'])}/; done; "
        f"mv *.pdf {q(st['docs'])}/", None),
    "files.backup": lambda st: (f"cp {q(st['file'])} {q(st['file'] + '.bak')}", None),
    "files.delete": lambda st: (f"rm {q(st['dir'])}/*.tmp", None),
    "files.moverename": lambda st: (f"mv {q(st['src'])} {q(st['dest'])}", None),
    "files.copydir": lambda st: (f"cp -r {q(st['saves'])} {q(st['backup'])}", None),
    "files.removedir": lambda st: (f"rm -r {q(st['old'])}", None),
}
