# Project Vital Source — AnarchyGames

Source of truth for the course. Changes to anything here get an entry in DECISIONS.md.

## The problem

New Linux users don't know where to start, and they don't remember commands they
don't care about. "If they don't know how it will benefit them, they won't care, and
if they don't care they won't remember."

## The method

1. **Ten core skills (plus lesson zero).** Drill each one alone until it is automatic.
2. **Combinations.** Then drill the skills chained together until the chains are automatic.
3. **Problem first, command second.** Every lesson and every drill opens with a real
   situation ("your disk is full", "where did I save that resume") and only then
   introduces the command that gets you out of it.
4. **Grade the result, not the keystrokes.** The checker inspects the resulting state
   (files, directories, cwd, an answer), so any correct method passes.
5. **Randomize every rep.** New names, sizes and layouts each time, so learners
   memorize the skill, not the answer.
6. **Fluency gates.** A lesson unlocks the next only after N clean reps under a time
   target. Right but slow means it isn't burned in yet.
7. **A disposable sandbox.** Mistakes (even `rm -rf`) cost nothing; reset is instant.

## The skills

| # | Skill | Commands | Hook |
|---|-------|----------|------|
| 0 | Help yourself | `tldr`, `--help \| grep`, `man` + `/ n q G`, `man -k`, Tab, Ctrl-R | "You'll never memorize everything. You'll learn to look things up fast." |
| 1 | Navigate | `pwd`, `cd`, `ls -la`, `~`, `..`, absolute vs relative | "Where am I, and how do I get there?" |
| 2 | Manipulate files | `mkdir`, `touch`, `cp`, `mv`, `rm`, globs | "Clean up the mess in Downloads." |
| 3 | Read files | `cat`, `less`, `head`, `tail -f` | "Something broke, and the answer is in a text file." |
| 4 | Find things | `find`, `grep -r` | "I know it's here somewhere." |
| 5 | Inspect | `du -sh`, `df -h`, `stat`, `file`, `wc` | "What is this, and why is it so big?" |
| 6 | Permissions | reading `ls -l`, `chmod`, `chown`, `sudo` | "Permission denied." |
| 7 | Pipes and redirection | `\|`, `>`, `>>`, `sort`, `uniq`, `cut` | "Turn ten commands into one answer." |
| 8 | Get and install software | `curl`/`wget`, `sha256sum`, `tar`, `apt`, `dpkg -L` | "Install a game from our repo." |
| 9 | Processes | `ps`, `top`, `kill`, Ctrl-C/Ctrl-Z, `jobs` | "It's frozen and eating the CPU." |
| 10 | Edit a config file | `nano`, enough vim to escape | "Change one setting." |

Later (level 2): `ssh`, `systemctl`, `journalctl`.

### Lesson 0: man pages

The pain point: man pages put too much in front of you, and people don't know how to read
them. The answer is to teach searching a page, not reading it:
- Ask in this order: `tldr cmd` → `cmd --help | grep word` → `man cmd` → `man -k word`.
- Inside man, four keys: `/` search, `n` next, `q` quit, `G` end (EXAMPLES).
- The skeleton: NAME, SYNOPSIS, DESCRIPTION, OPTIONS, EXAMPLES.
- Decoding SYNOPSIS: `[ ]` optional, `...` repeatable, `|` choose one, bold = literal,
  underline = your value.
- Timed scavenger hunts: "make `ls` sort by size, using only `man ls`."

## The AnarchyGames repo (skill 8)

A signed apt repo of small games, used to teach how repos and registries work.

Games: an asteroids-like game, a top-down space maze racer (beat the clock), and
In the Black. The first two are terminal games so they run inside the sandbox; In the
Black (HTML5) ships as a `.deb` that installs files, a launcher and a `.desktop`
entry, as the graduation install on the learner's real machine.

Lesson arc:
1. Download a `.deb` into `~/Downloads`, check `sha256sum`, `apt install ./file.deb`.
2. Add the repo (sources line + signing key), `apt update`, `apt search`, `apt show`, `apt install`.
3. Publish v1.1 to the repo; the learner runs `apt upgrade` and sees it arrive.
4. A dependency (e.g. `anarchy-sounds`) gets pulled in automatically.
5. `dpkg -L`, `du`, `apt remove` / `purge` / `autoremove`.
6. A tampered package fails its checksum: don't install it.
7. Compare pip, npm, Docker Hub and Flathub: a list of packages, a source to fetch from, a trust mechanism.

The repo starts local inside the sandbox. Hosting it publicly on anarchygames.org is
publishing and is the user's call.

## Style

Match anarchygames.org ("Blade Runner billboard"). Source of the tokens:
`AnarchySC.github.io/assets/css/main.css`.

- Colors: bg `#05080e`, surface `#0a0e18`, card `#0d1220`, text `#c8ccd4`, muted
  `#6a7080`, border `#141c2e`, neon orange `#E85D04`, amber `#FAA307`, gold `#FFD000`,
  cyan `#00d4ff`, blue `#4a7ab5`, pink `#ff2d7b`, green `#3fb950`.
- Square corners, neon glows, CRT scanlines and film grain.
- Fonts: Codex (display), EB Garamond (headings), Inter (body), JetBrains Mono (code).

The style also applies to the sandbox (prompt, login banner, `LS_COLORS`), the
terminal games and the repo landing page.

## Phases

1. **Sandbox + drill engine + lessons 0-2.** See PHASE1_PLAN.md.
2. **Lessons 3-7** and the first combination missions.
3. **AnarchyGames repo + games + lesson 8.**
4. **Lessons 9-10 + the combination campaign** (story missions such as "the disk is full").
5. **Course website** section on anarchygames.org, plus the learner distribution decision
   (see NOTES.md).
