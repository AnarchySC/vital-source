"""Every exercise: a real shell solve passes, doing nothing fails, setups vary by seed.

Solutions run in real bash with real coreutils, so a check that only passes for some
imagined command would fail here.
"""

import json
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from drill.engine import Ctx, reset_lab  # noqa: E402
from drill.lessons import LESSONS  # noqa: E402
from drill.lessons import l00_help  # noqa: E402
from solutions import OUT, SOLUTIONS, q  # noqa: E402

ALL = [ex for lesson in LESSONS for ex in lesson.exercises]
SEEDS = range(12)


# Plausible mistakes a learner makes; each must fail.
MISTAKES = {
    "files.delete": lambda st: f"rm {q(st['dir'])}/*tmp*",
    "files.sort": lambda st: f"mv {q(st['dl'])}/* {q(st['pics'])}/",
    "files.backup": lambda st: f"mv {q(st['file'])} {q(st['file'] + '.bak')}",
    "files.moverename": lambda st: f"cp {q(st['src'])} {q(st['dest'])}",
    "files.copydir": lambda st: f"mkdir {q(st['backup'])} && cp -r {q(st['saves'])} {q(st['backup'])}",
    "files.removedir": lambda st: f"rm -r {q(Path(st['old']).parent)}/*",
    "help.tldr": lambda st: f"cd {q(st['dl'])}/.. && tar xf Downloads/{q(st['name'])}",
}


def run(script, start, home):
    marker = "__DRILL_CWD__"
    proc = subprocess.run(
        ["bash", "-c", f"cd {q(start)} && {script}; echo {marker}\"$(pwd -P)\""],
        capture_output=True, text=True, env={"HOME": str(home), "PATH": "/usr/bin:/bin", "LC_ALL": "C"},
    )
    out, _, cwd = proc.stdout.rpartition(marker)
    return Path(cwd.strip()), out.strip()


def fresh(tmp_path, ex, seed):
    home = tmp_path / f"home-{ex.id}-{seed}"
    home.mkdir()
    ctx = Ctx(home)
    reset_lab(ctx)
    st = ex.setup(random.Random(seed), ctx)
    return ctx, st


def test_every_exercise_has_a_solution():
    assert {ex.id for ex in ALL} == set(SOLUTIONS)


@pytest.mark.parametrize("ex", ALL, ids=lambda e: e.id)
@pytest.mark.parametrize("seed", SEEDS)
def test_correct_solve_passes(tmp_path, ex, seed):
    ctx, st = fresh(tmp_path, ex, seed)
    script, answer = SOLUTIONS[ex.id](st)
    cwd = ctx.home
    if script:
        cwd, out = run(script, st.get("start", ctx.home), ctx.home)
        if answer is OUT:
            answer = out
    res = ex.check(st, ctx, cwd, answer)
    assert res.ok, res.msg


@pytest.mark.parametrize("ex", ALL, ids=lambda e: e.id)
@pytest.mark.parametrize("seed", SEEDS)
def test_doing_nothing_fails(tmp_path, ex, seed):
    ctx, st = fresh(tmp_path, ex, seed)
    res = ex.check(st, ctx, ctx.home, "nope" if ex.answer else None)
    assert not res.ok
    assert res.msg


@pytest.mark.parametrize("ex_id", sorted(MISTAKES))
@pytest.mark.parametrize("seed", SEEDS)
def test_mistakes_fail(tmp_path, ex_id, seed):
    ex = next(e for e in ALL if e.id == ex_id)
    ctx, st = fresh(tmp_path, ex, seed)
    cwd, _ = run(MISTAKES[ex_id](st), ctx.home, ctx.home)
    res = ex.check(st, ctx, cwd, None)
    assert not res.ok
    assert res.msg


@pytest.mark.parametrize("ex", ALL, ids=lambda e: e.id)
def test_setups_vary(tmp_path, ex):
    states = {json.dumps(fresh(tmp_path, ex, s)[1], sort_keys=True).replace(str(tmp_path), "") for s in SEEDS}
    assert len(states) >= 3


@pytest.mark.parametrize("ex", ALL, ids=lambda e: e.id)
def test_hints_render(tmp_path, ex):
    ctx, st = fresh(tmp_path, ex, 0)
    assert ex.hint(st, ctx).strip()


# --- the facts the help lesson teaches must be true of the installed tools ---

def gnu():
    """The sandbox is Debian with GNU tools. Some hosts (Ubuntu 25.10+) ship uutils,
    whose help text differs, so the fact checks only mean something against GNU."""
    try:
        return "GNU" in subprocess.run(["ls", "--version"], capture_output=True, text=True).stdout
    except OSError:
        return False


def help_text(cmd):
    if not gnu():
        pytest.skip("not GNU coreutils; run these in the sandbox image")
    if not shutil.which(cmd):
        pytest.skip(f"{cmd} not installed")
    return subprocess.run([cmd, "--help"], capture_output=True, text=True,
                          env={"LC_ALL": "C", "PATH": "/usr/bin:/bin"}).stdout


def option_tokens(text):
    return set(re.findall(r"(?<![\w-])(--?[\w-]+)", text))


@pytest.mark.parametrize("item", l00_help.HELP_POOL + l00_help.MAN_POOL, ids=lambda i: f"{i[0]}{i[2][0]}")
def test_flags_exist(item):
    cmd, _, answers, _ = item
    tokens = option_tokens(help_text(cmd))
    for a in answers:
        assert a.split("=")[0] in tokens, f"{cmd} has no {a}"


@pytest.mark.parametrize("item", l00_help.HELP_POOL, ids=lambda i: f"{i[0]}{i[2][0]}")
def test_grep_hint_finds_the_flag(item):
    """The hint says `cmd --help | grep -i word`; the flag must be on a matching line."""
    cmd, _, answers, word = item
    lines = [l for l in help_text(cmd).splitlines() if word.lower() in l.lower()]
    assert any(answers[0] in option_tokens(l) for l in lines), f"grep -i {word} doesn't show {answers[0]}"


@pytest.mark.parametrize("item", l00_help.MAN_POOL, ids=lambda i: f"{i[0]}{i[2][0]}")
def test_man_search_lands_near_the_flag(item):
    """The hint says /word lands on the flag's line or just below it."""
    cmd, _, answers, word = item
    lines = help_text(cmd).splitlines()
    hits = [i for i, l in enumerate(lines) if word.lower() in l.lower()]
    assert any(answers[0] in option_tokens(" ".join(lines[max(0, i - 2):i + 1])) for i in hits), \
        f"/{word} isn't near {answers[0]}"


@pytest.mark.parametrize("item", l00_help.APROPOS_POOL, ids=lambda i: i[2])
def test_apropos_finds_the_command(item):
    _, kw, cmd = item
    if not gnu():
        pytest.skip("not GNU coreutils; run these in the sandbox image")
    proc = subprocess.run(["man", "-k", kw], capture_output=True, text=True) if shutil.which("man") else None
    if not proc or proc.returncode != 0:
        pytest.skip("no man -k database here")
    assert any(l.startswith(f"{cmd} (") for l in proc.stdout.splitlines())
