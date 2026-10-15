# Project Vital Source — AnarchyGames

Learn Linux in the terminal: drill each core skill until it's automatic, then drill them together.

You need Docker. Then:

    git clone https://github.com/AnarchySC/vital-source
    cd vital-source
    bin/learn-linux            enter the sandbox (the first run builds it)
    bin/learn-linux --reset    fresh sandbox, progress kept
    bin/learn-linux --rebuild  rebuild the image after changes

Inside: `drill list`, then `drill start 0`.

Status: lessons 0-2 (Help yourself, Navigate, Move things around) are playable.
Lessons 3-10 and the AnarchyGames package repo are next.

Tests:

    cd drill && python3 -m pytest -q    # host (fact checks skip unless GNU coreutils)
    drill/tests/smoke.sh                # full mastery run through the real CLI, in the image

Plan and status: PLAN.md, PROGRESS.md, DECISIONS.md, NOTES.md.
