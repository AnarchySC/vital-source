import os
from pathlib import Path

from . import engine, ui
from .engine import STREAK_TO_MASTER, Ctx
from .lessons import LESSONS
from .progress import Progress

USAGE = """
`drill list`            the lessons and what's unlocked
`drill start N`         start drilling lesson N
`drill`                 show the task you're on
`drill check`           check your work
`drill answer ...`      send an answer, for tasks that ask a question
`drill hint`            get a hint (that rep won't count toward your streak)
`drill skip`            new rep (resets your streak)
`drill intro [N]`       reread a lesson's introduction
`drill stats`           your streaks and best times
"""


def cwd_now():
    try:
        return Path(os.getcwd()).resolve()
    except FileNotFoundError:
        return None


def hand_off_cd(ctx: Ctx, st: dict, cwd):
    """Ask the shell wrapper (in ~/.bashrc) to move the learner after we exit."""
    target = st.get("start")
    if not target:
        lab = ctx.lab.resolve()
        if cwd is None or cwd == lab or lab in cwd.parents:
            target = str(ctx.home)
    if target:
        try:
            Path(f"/tmp/drill-cd-{os.getuid()}").write_text(target)
        except OSError:
            pass


def show_task(lesson, prog):
    cur = prog.data["current"]
    ex = lesson.find(cur["exercise"])
    rec = prog.ex(ex.id)
    right = "MASTERED" if rec["mastered"] else ""
    print()
    print(ui.bar(f"LESSON {lesson.number} · {lesson.name.upper()}",
                 right) + (" " if right else "") + ui.streak(rec["streak"], STREAK_TO_MASTER))
    print("  " + ui.c(ui.CYAN, ex.title, bold=True) + ui.muted(f"   target {ex.target}s"))
    print()
    print(ui.para(cur["state"]["prompt"]))
    print()
    first = "`drill answer <your answer>`" if ex.answer else "`drill check` when you're done"
    print(ui.muted("  ") + ui.code(first) + ui.muted("  ·  ") + ui.code("`drill hint`")
          + ui.muted("  ·  ") + ui.code("`drill skip`"))
    print()


def show_intro(lesson):
    print()
    print(ui.bar(f"LESSON {lesson.number} · {lesson.name.upper()}"))
    print("  " + ui.c(ui.CYAN, lesson.hook, bold=True))
    print()
    print(ui.para(lesson.intro))
    print()


def lesson_arg(args, prog):
    if args:
        try:
            n = int(args[0])
        except ValueError:
            n = -1
        if not 0 <= n < len(LESSONS):
            print(ui.bad(f"There's no lesson {args[0]}. Lessons run 0 to {len(LESSONS) - 1}."))
            return None
        return LESSONS[n]
    if prog.data["current"]:
        return LESSONS[prog.data["current"]["lesson"]]
    print(ui.bad("Which lesson? For example: ") + ui.code("`drill start 0`"))
    return None


def cmd_start(args, prog, ctx):
    lesson = lesson_arg(args, prog)
    if lesson is None:
        return 1
    if not engine.unlocked(LESSONS, prog, lesson.number):
        prev = LESSONS[lesson.number - 1]
        print(ui.bad(f"Lesson {lesson.number} unlocks when you master lesson {prev.number} ({prev.name})."))
        return 1
    if lesson.number not in prog.data["intro_seen"]:
        show_intro(lesson)
        prog.data["intro_seen"].append(lesson.number)
    cwd = cwd_now()
    cur = engine.new_rep(lesson, prog, ctx)
    hand_off_cd(ctx, cur["state"], cwd)
    show_task(lesson, prog)
    return 0


def cmd_grade(prog, ctx, answer):
    cur = prog.data["current"]
    if not cur:
        print(ui.bad("No task running. Start one with ") + ui.code("`drill start N`"))
        return 1
    lesson = LESSONS[cur["lesson"]]
    ex = lesson.find(cur["exercise"])
    if ex.answer and answer is None:
        print(ui.code("  This one wants an answer: `drill answer <your answer>`"))
        return 1
    if not ex.answer and answer is not None:
        print(ui.code("  This one is checked by looking at your files. Do it, then `drill check`."))
        return 1

    cwd = cwd_now()
    out = engine.grade(lesson, prog, ctx, cwd, answer)
    print()
    if not out.result.ok:
        print("  " + ui.bad(out.result.msg))
        print(ui.muted("    Streak reset. Fix it and check again, or take a hint."))
        print()
        return 1

    rec = prog.ex(ex.id)
    secs = f"{out.elapsed:.1f}s"
    if out.clean:
        print("  " + ui.ok(ui.c(ui.GREEN, "CLEAN", bold=True) + "  " + secs)
              + "  " + ui.streak(rec["streak"], STREAK_TO_MASTER))
    elif out.slow and not cur["failed"] and not cur["hinted"]:
        print("  " + ui.ok(f"Correct, in {secs}. The target is {ex.target}s: right but slow means it "
                           "isn't burned in yet. Your streak holds."))
    else:
        print("  " + ui.ok("Correct. A rep after a miss or a hint doesn't count toward the streak."))
    if out.result.msg:
        print(ui.para(out.result.msg, indent=4))
    if out.newly_mastered:
        print()
        print("  " + ui.c(ui.GOLD, "MASTERED", bold=True) + "  " + ex.title)

    if out.lesson_done:
        print()
        print(ui.bar(f"LESSON {lesson.number} MASTERED"))
        nxt = lesson.number + 1
        if nxt < len(LESSONS):
            print(ui.code(f"  Lesson {nxt} ({LESSONS[nxt].name}) is unlocked: `drill start {nxt}`"))
        else:
            print(ui.muted("  That's every lesson there is so far."))
        print(ui.code(f"  Or keep this one sharp: `drill start {lesson.number}`"))
        print()
        prog.data["current"] = None
        return 0

    new = engine.new_rep(lesson, prog, ctx, last=ex.id)
    hand_off_cd(ctx, new["state"], cwd)
    show_task(lesson, prog)
    return 0


def cmd_hint(prog, ctx):
    cur = prog.data["current"]
    if not cur:
        print(ui.bad("No task running."))
        return 1
    lesson = LESSONS[cur["lesson"]]
    text = engine.take_hint(lesson, prog, ctx)
    print()
    print(ui.para(text))
    print()
    print(ui.muted("  This rep won't count toward your streak. The next one will."))
    print()
    return 0


def cmd_skip(prog, ctx):
    cur = prog.data["current"]
    if not cur:
        print(ui.bad("No task running."))
        return 1
    lesson = LESSONS[cur["lesson"]]
    engine.skip(lesson, prog)
    cwd = cwd_now()
    new = engine.new_rep(lesson, prog, ctx, last=cur["exercise"])
    hand_off_cd(ctx, new["state"], cwd)
    show_task(lesson, prog)
    return 0


def cmd_list(prog):
    print()
    for lesson in LESSONS:
        done = sum(prog.ex(e.id)["mastered"] for e in lesson.exercises)
        total = len(lesson.exercises)
        if engine.lesson_mastered(lesson, prog):
            mark, color = "✔", ui.GREEN
        elif engine.unlocked(LESSONS, prog, lesson.number):
            mark, color = "▸", ui.AMBER
        else:
            mark, color = "·", ui.DIM
        print(f"  {ui.c(color, mark)} {ui.c(color, f'{lesson.number:>2}', bold=True)}  "
              f"{ui.c(ui.TEXT, f'{lesson.name:<20}')} {ui.muted(f'{done}/{total}')}   {ui.muted(lesson.hook)}")
    print()
    print(ui.muted("  More lessons are on the way: reading files, finding things, permissions, pipes,"))
    print(ui.muted("  installing software, processes and editing configs."))
    print()
    return 0


def cmd_stats(prog):
    print()
    for lesson in LESSONS:
        if not engine.unlocked(LESSONS, prog, lesson.number):
            continue
        print(ui.bar(f"LESSON {lesson.number} · {lesson.name.upper()}"))
        for ex in lesson.exercises:
            rec = prog.ex(ex.id)
            best = f"{rec['best']}s" if rec["best"] is not None else "-"
            tag = ui.c(ui.GOLD, "MASTERED") if rec["mastered"] else ""
            nums = f"best {best:>6}  target {ex.target}s  reps {rec['reps']:>3}"
            print(f"    {ui.c(ui.TEXT, f'{ex.title:<30}')} {ui.streak(rec['streak'], STREAK_TO_MASTER)}  "
                  f"{ui.muted(nums)}  {tag}")
        print()
    return 0


def main(argv):
    ctx = Ctx(Path.home())
    prog = Progress()
    cmd, args = (argv[0], argv[1:]) if argv else ("show", [])

    if cmd == "show":
        cur = prog.data["current"]
        if cur:
            show_task(LESSONS[cur["lesson"]], prog)
            return 0
        print(ui.para(USAGE))
        return 0
    if cmd in ("help", "-h", "--help"):
        print(ui.para(USAGE))
        return 0
    if cmd == "list":
        return cmd_list(prog)
    if cmd == "stats":
        return cmd_stats(prog)
    if cmd == "intro":
        lesson = lesson_arg(args, prog)
        if lesson is None:
            return 1
        show_intro(lesson)
        return 0

    if cmd == "start":
        rc = cmd_start(args, prog, ctx)
    elif cmd == "check":
        rc = cmd_grade(prog, ctx, None)
    elif cmd == "answer":
        rc = cmd_grade(prog, ctx, " ".join(args))
    elif cmd == "hint":
        rc = cmd_hint(prog, ctx)
    elif cmd == "skip":
        rc = cmd_skip(prog, ctx)
    else:
        print(ui.bad(f"Unknown command: {cmd}"))
        print(ui.para(USAGE))
        return 1
    prog.save()
    return rc
