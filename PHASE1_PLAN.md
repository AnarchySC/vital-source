# Phase 1 — Sandbox, drill engine, lessons 0-2

## §0 Locked decisions

| Decision | Choice | Why | Rejected |
|----------|--------|-----|----------|
| Sandbox | Docker image on Debian 13 (trixie) slim | Instant reset, runs on this machine today, apt-based to match lesson 8 | In-browser VM (v86): zero install for learners, but slow to build and test against; revisit in phase 5 |
| Distro family | Debian/apt | Most common beginner target; one family only | Fedora/dnf, Arch |
| Drill engine | Python 3, stdlib only, installed in the image as `drill` | Already in Debian, easy to write state checks | Bash (checks get unreadable), Go (build step for no gain) |
| Grading | Checks the end state (files, cwd, `drill answer`) | Any correct method passes | Matching typed commands |
| Progress | `~/.drill/progress.json` on a named Docker volume | Survives sandbox resets | Inside the container (lost on reset) |
| Man pages | Remove slim's dpkg path excludes, install `man-db`, `manpages`, plus a tldr client with a pre-seeded cache | Slim images strip man pages; lesson 0 needs them offline | Online-only tldr |

## Steps

1. **Image.** `sandbox/Dockerfile`: trixie-slim, restore man pages, install core tools
   (`less`, `nano`, `vim-tiny`, `file`, `tree`, `curl`, tldr client), and create a
   non-root `learner` user with sudo.
2. **Theme.** `sandbox/theme/`: truecolor PS1 (orange user, cyan path), an AnarchyGames
   login banner, and `LS_COLORS` in the site palette.
3. **Launcher.** `bin/learn-linux`: build if needed and run with the progress volume.
   `--reset` wipes the sandbox but keeps progress.
4. **Drill engine.** `drill/`: CLI with `list`, `start <lesson>`, `check`, `answer <x>`,
   `hint`, `skip`, `stats`. Each exercise is a module with `setup(rng, home)`,
   a scenario prompt, and `check(...) -> (ok, feedback)`. Timer per rep; mastery =
   5 consecutive passes, each under the exercise's time target.
5. **Lesson 0: help.** Exercises: find the flag with `--help | grep`, find the flag in
   `man` using `/`, decode a SYNOPSIS line, `man -k` to find which command does X.
6. **Lesson 1: navigate.** Exercises: report `pwd`, go to a randomized target
   (absolute, relative, `~`, `..`), find the hidden file with `ls -a`, go back with `cd -`.
7. **Lesson 2: files.** Exercises: build a requested folder tree, sort a messy
   Downloads by extension with globs, rename/move, delete only the matching files.
8. **Engine tests.** pytest for every exercise: a scripted correct solve passes, a
   wrong solve fails, and setup is different across seeds.
9. **Smoke.** Build the image, run each lesson once by hand.

## Files

```
sandbox/Dockerfile
sandbox/theme/{bashrc,motd,dircolors}
bin/learn-linux
drill/drill/__main__.py, engine.py, progress.py, ui.py
drill/drill/lessons/{l00_help,l01_navigate,l02_files}.py
drill/tests/test_lessons.py
```

## Out of scope

Lessons 3-10, combinations, the apt repo and games, the website, publishing anything.

## Done when

- [x] `bin/learn-linux` drops you into a themed shell with working `man` and `tldr`
- [x] `drill start 0|1|2` runs randomized reps, checks results, tracks mastery
- [x] Progress survives `--reset`
- [x] All exercise tests pass
- [x] Each lesson run to mastery through the real CLI (automated: drill/tests/smoke.sh). Not yet played by a human.
