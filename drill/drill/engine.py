"""Exercise model, rep lifecycle and mastery rules."""

import os
import random
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path

STREAK_TO_MASTER = 5


@dataclass
class Ctx:
    """Where a rep happens. Tests point home at a temp dir."""

    home: Path

    @property
    def lab(self) -> Path:
        return self.home / "lab"

    def show(self, path) -> str:
        """Path as the learner would write it, with ~ for home."""
        p, h = str(path), str(self.home)
        if p == h:
            return "~"
        if p.startswith(h + "/"):
            return "~" + p[len(h):]
        return p

    def resolve(self, text: str) -> Path:
        text = text.strip()
        if text == "~" or text.startswith("~/"):
            text = str(self.home) + text[1:]
        return Path(text)


@dataclass
class Result:
    ok: bool
    msg: str = ""


class Exercise:
    id = ""
    title = ""
    target = 30          # seconds for a clean rep
    answer = False       # graded by `drill answer` instead of by the files

    def setup(self, rng: random.Random, ctx: Ctx) -> dict:
        """Build the scenario under ctx.lab and return JSON-safe state.

        State must hold "prompt"; "start" (a path) drops the learner there.
        """
        raise NotImplementedError

    def check(self, st: dict, ctx: Ctx, cwd, answer) -> Result:
        raise NotImplementedError

    def hint(self, st: dict, ctx: Ctx) -> str:
        raise NotImplementedError


@dataclass
class Lesson:
    number: int
    name: str
    hook: str
    intro: str
    exercises: list = field(default_factory=list)

    def find(self, ex_id):
        for ex in self.exercises:
            if ex.id == ex_id:
                return ex
        return None


def reset_lab(ctx: Ctx):
    if ctx.lab.exists():
        # Learners chmod things in later lessons; make sure the wipe can't stall.
        for root, dirs, _ in os.walk(ctx.lab):
            for d in dirs:
                try:
                    os.chmod(os.path.join(root, d), 0o755)
                except OSError:
                    pass
        shutil.rmtree(ctx.lab)
    ctx.lab.mkdir(parents=True)


def lesson_mastered(lesson: Lesson, prog) -> bool:
    return all(prog.ex(e.id)["mastered"] for e in lesson.exercises)


def unlocked(lessons, prog, number) -> bool:
    if number == 0 or os.environ.get("DRILL_UNLOCK_ALL"):
        return True
    prev = lessons[number - 1]
    return lesson_mastered(prev, prog)


def pick(lesson: Lesson, prog, rng: random.Random, last=None) -> Exercise:
    todo = [e for e in lesson.exercises if not prog.ex(e.id)["mastered"]]
    pool = todo or lesson.exercises
    if len(pool) > 1 and last:
        pool = [e for e in pool if e.id != last] or pool
    return rng.choice(pool)


def new_rep(lesson: Lesson, prog, ctx: Ctx, last=None) -> dict:
    ex = pick(lesson, prog, random.Random(), last)
    seed = random.randrange(2 ** 32)
    reset_lab(ctx)
    st = ex.setup(random.Random(seed), ctx)
    cur = {
        "lesson": lesson.number,
        "exercise": ex.id,
        "seed": seed,
        "state": st,
        "started": time.time(),
        "failed": False,
        "hinted": False,
    }
    prog.data["current"] = cur
    return cur


@dataclass
class Outcome:
    result: Result
    elapsed: float = 0.0
    clean: bool = False
    slow: bool = False
    newly_mastered: bool = False
    lesson_done: bool = False


def grade(lesson: Lesson, prog, ctx: Ctx, cwd, answer) -> Outcome:
    cur = prog.data["current"]
    ex = lesson.find(cur["exercise"])
    rec = prog.ex(ex.id)
    res = ex.check(cur["state"], ctx, cwd, answer)
    if not res.ok:
        cur["failed"] = True
        rec["streak"] = 0
        return Outcome(res)

    elapsed = time.time() - cur["started"]
    slow = elapsed > ex.target
    clean = not cur["failed"] and not cur["hinted"] and not slow
    rec["reps"] += 1
    rec["passes"] += 1
    if not cur["failed"] and not cur["hinted"]:
        if rec["best"] is None or elapsed < rec["best"]:
            rec["best"] = round(elapsed, 1)
    out = Outcome(res, elapsed=elapsed, clean=clean, slow=slow)
    if clean:
        rec["streak"] += 1
        if rec["streak"] >= STREAK_TO_MASTER and not rec["mastered"]:
            rec["mastered"] = True
            out.newly_mastered = True
            out.lesson_done = lesson_mastered(lesson, prog)
    return out


def take_hint(lesson: Lesson, prog, ctx: Ctx) -> str:
    cur = prog.data["current"]
    ex = lesson.find(cur["exercise"])
    if not cur["hinted"]:
        cur["hinted"] = True
        prog.ex(ex.id)["streak"] = 0
    return ex.hint(cur["state"], ctx)


def skip(lesson: Lesson, prog):
    cur = prog.data["current"]
    rec = prog.ex(cur["exercise"])
    rec["streak"] = 0
    rec["reps"] += 1
