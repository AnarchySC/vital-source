"""Smoke helper: print a shell line that solves the current rep, using the real CLI.

Used only by tests/smoke.sh inside the image. Prints "drill answer ..." or the shell
commands followed by "drill check", so the shell wrapper and cd handoff get exercised.
"""

import json
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from solutions import OUT, SOLUTIONS  # noqa: E402

cur = json.loads(Path("/var/lib/drill/progress.json").read_text())["current"]
if not cur:
    print("true")
    sys.exit()
st = cur["state"]
script, answer = SOLUTIONS[cur["exercise"]](st)
if answer is OUT:
    print(f"drill answer \"$( {script} )\"")
elif answer is not None:
    print("drill answer " + shlex.quote(answer))
else:
    print(f"{script}; drill check")
