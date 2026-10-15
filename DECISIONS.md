# Decisions

## ADR-001 Problem-first, state-graded, randomized drills (2026-10-15)
User principle: learners won't remember what they don't care about. Every drill opens with a
real situation; grading checks results, not keystrokes; every rep is randomized.

## ADR-002 Own apt repo of AnarchyGames titles for skill 8 (2026-10-15)
Teaches repos, registries, signing, upgrades and dependencies with real packages. Starts local.

## ADR-003 Visual style matches anarchygames.org (2026-10-15)
User request. Tokens taken from the site's main.css; see PLAN.md.

## ADR-004 Phase 1 stack (2026-10-15)
Docker + Debian trixie-slim sandbox, Python stdlib drill engine. Full rationale in
PHASE1_PLAN.md §0.

## ADR-005 Streak rules (2026-10-15)
A clean rep is a pass with no failed check, no hint and under the target time. Clean reps
build the streak; 5 masters the exercise. A fail, a hint or a skip resets the streak. A
correct but slow pass neither adds nor resets ("right but slow isn't burned in yet"), so
beginners aren't knocked back to zero while they speed up. A lesson is mastered when
every exercise in it is; that unlocks the next. `DRILL_UNLOCK_ALL=1` bypasses locks for testing.

## ADR-006 Progress at /var/lib/drill, not in ~ (2026-10-15)
Lesson 2 teaches rm -r; progress inside home could be deleted by an exercise gone wrong.
/var/lib/drill is a named Docker volume (learn-linux-progress) owned by learner.

## ADR-007 Help facts are verified against GNU coreutils only (2026-10-15)
This dev host runs Ubuntu with uutils (Rust) coreutils, whose --help text differs from GNU.
The sandbox is Debian (GNU), so the flag/man -k fact tests skip on non-GNU hosts and the
suite is run inside the image as the real check. See NOTES.md for the learner impact.
