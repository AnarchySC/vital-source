import io
import tarfile

from .. import world
from ..engine import Exercise, Lesson, Result

INTRO = """
Nobody remembers every option of every command. People who are fast in a terminal
aren't the ones who memorized the most. They're the ones who can look something up in
ten seconds. That's this lesson.

Ask in this order, and stop as soon as you have your answer:

    1. `tldr tar`              examples of the common uses
    2. `ls --help | grep size`  the command's own short help, filtered
    3. `man ls`                 the full manual
    4. `man -k space`           "which command does this?"

Don't read a man page. Search it. Inside one, you only need four keys:

    /word   search for word        n   jump to the next match
    G       jump to the end        q   quit
            (EXAMPLES usually live at the end)

Every man page has the same skeleton: NAME, SYNOPSIS, DESCRIPTION, OPTIONS, often
EXAMPLES. Read NAME, then jump to what you need.

The SYNOPSIS line looks like code, but it's a small, fixed notation:

    [THING]     optional, you can leave it out
    THING...    you can give more than one
    a|b         pick one
    bold        type it exactly as shown
    underlined  replace it with your own value

Two more habits: press Tab to finish a command or file name, and Ctrl-R to search
everything you've typed before.
"""


# (command, what you want, accepted answers, a word that finds it in --help)
HELP_POOL = [
    ("ls", "list the biggest files first", ["-S", "--sort=size"], "size"),
    ("ls", "list the most recently changed files first", ["-t", "--sort=time"], "newest"),
    ("ls", "show hidden files (the ones whose names start with a dot)", ["-a", "--all", "-A", "--almost-all"], "starting"),
    ("ls", "reverse the order of the listing", ["-r", "--reverse"], "reverse"),
    ("cp", "ask before it overwrites a file that already exists", ["-i", "--interactive"], "overwrite"),
    ("cp", "copy a whole folder and everything inside it", ["-r", "-R", "--recursive"], "recursive"),
    ("cp", "print the name of each file as it copies it", ["-v", "--verbose"], "explain"),
    ("mkdir", "create a folder along with any missing folders above it, in one go", ["-p", "--parents"], "parent"),
    ("rm", "ask before every single removal", ["-i"], "prompt"),
    ("head", "show a number of lines other than the default 10", ["-n", "--lines"], "lines"),
    ("wc", "count only the lines in a file", ["-l", "--lines"], "lines"),
    ("sort", "sort numbers by value, so 10 comes after 9 instead of after 1", ["-n", "--numeric-sort"], "numeric"),
    ("grep", "match words whether they're in upper or lower case", ["-i", "--ignore-case"], "case"),
    ("grep", "show the line number next to each match", ["-n", "--line-number"], "number"),
    ("du", "print one total for a folder instead of a line for every folder inside it", ["-s", "--summarize"], "total"),
]

MAN_POOL = [
    ("tail", "keep watching a log and print new lines as they're written", ["-f", "--follow"], "follow"),
    ("ls", "list a folder itself instead of what's inside it", ["-d", "--directory"], "themselves"),
    ("cp", "never overwrite a file that already exists", ["-n", "--no-clobber"], "overwrite"),
    ("rm", "also remove empty folders", ["-d", "--dir"], "empty"),
    ("sort", "drop duplicate lines while it sorts", ["-u", "--unique"], "equal"),
    ("sort", "sort sizes like 2K, 5M and 1G in the right order", ["-h", "--human-numeric-sort"], "human"),
    ("grep", "show only the lines that do NOT match", ["-v", "--invert-match"], "invert"),
    ("grep", "list just the names of the files that contain a match", ["-l", "--files-with-matches"], "files-with"),
    ("uniq", "count how many times each line appears in a row", ["-c", "--count"], "occurrences"),
    ("df", "show free space in K, M and G instead of raw blocks", ["-h", "--human-readable"], "human"),
    ("touch", "update a file's time without creating it if it doesn't exist", ["-c", "--no-create"], "create"),
    ("wc", "count words", ["-w", "--words"], "word"),
]

# (what you need, a keyword that finds it with man -k, the command)
APROPOS_POOL = [
    ("estimates how much disk space files and folders take up", "space usage", "du"),
    ("shows the first part of a file", "first part", "head"),
    ("shows the last part of a file", "last part", "tail"),
    ("removes empty folders", "remove empty", "rmdir"),
    ("changes a file's timestamps", "timestamps", "touch"),
    ("prints the name of the folder your shell is in", "working directory", "pwd"),
    ("reports or removes repeated lines in a file", "repeated", "uniq"),
    ("counts the lines, words and bytes in a file", "byte counts", "wc"),
    ("tells you what kind of file something really is", "file type", "file"),
    ("sorts the lines of a text file", "sort lines", "sort"),
]

# Real GNU SYNOPSIS lines. Each element: (name, optional, repeatable).
SYNOPSES = [
    ("ls", "ls [OPTION]... [FILE]...", [("FILE", True, True)]),
    ("mkdir", "mkdir [OPTION]... DIRECTORY...", [("DIRECTORY", False, True)]),
    ("touch", "touch [OPTION]... FILE...", [("FILE", False, True)]),
    ("rmdir", "rmdir [OPTION]... DIRECTORY...", [("DIRECTORY", False, True)]),
    ("head", "head [OPTION]... [FILE]...", [("FILE", True, True)]),
    ("cp", "cp [OPTION]... [-T] SOURCE DEST", [("SOURCE", False, False), ("DEST", False, False), ("-T", True, False)]),
    ("mv", "mv [OPTION]... [-T] SOURCE DEST", [("SOURCE", False, False), ("DEST", False, False), ("-T", True, False)]),
    ("ln", "ln [OPTION]... [-T] TARGET LINK_NAME", [("TARGET", False, False), ("LINK_NAME", False, False)]),
    ("du", "du [OPTION]... [FILE]...", [("FILE", True, True)]),
    ("grep", "grep [OPTION...] PATTERNS [FILE...]", [("PATTERNS", False, False), ("FILE", True, True)]),
]


def flag_answer(st, answer):
    a = (answer or "").strip().strip("'\"")
    if a in st["answers"]:
        return Result(True, f"`{st['cmd']} {st['answers'][0]}` does it.")
    if a and "-" + a in st["answers"]:
        return Result(False, f"Almost. Options start with a dash: {'-' + a}")
    return Result(False, f"That's not the option that does it. Look again in `{st['cmd']}`'s help.")


class HelpFlag(Exercise):
    id = "help.flag"
    title = "Ask the command itself"
    target = 60
    answer = True

    def setup(self, rng, ctx):
        cmd, need, answers, word = rng.choice(HELP_POOL)
        prompt = (f"You want `{cmd}` to {need}, and you don't know which option does that. "
                  f"Almost every command explains itself when you add --help, but the list "
                  f"is long. Filter it.\n\nFind the option and send it.")
        return {"cmd": cmd, "answers": answers, "word": word, "prompt": prompt}

    def check(self, st, ctx, cwd, answer):
        return flag_answer(st, answer)

    def hint(self, st, ctx):
        return (f"Pipe the help into grep to show only the lines with a useful word:\n\n"
                f"    `{st['cmd']} --help | grep -i {st['word']}`")


class ManFlag(Exercise):
    id = "help.man"
    title = "Search the manual"
    target = 90
    answer = True

    def setup(self, rng, ctx):
        cmd, need, answers, word = rng.choice(MAN_POOL)
        prompt = (f"You need `{cmd}` to {need}. Open its manual with `man {cmd}`. Don't read "
                  f"it top to bottom. Press / and type a word you'd expect near the answer, "
                  f"press Enter, use n to jump to the next match, and q to quit.\n\n"
                  f"Find the option and send it.")
        return {"cmd": cmd, "answers": answers, "word": word, "prompt": prompt}

    def check(self, st, ctx, cwd, answer):
        return flag_answer(st, answer)

    def hint(self, st, ctx):
        return (f"In `man {st['cmd']}`, type /{st['word']} and press Enter. The option is at the "
                f"start of the line the match is on, or just above it.")


class Apropos(Exercise):
    id = "help.apropos"
    title = "Which command does that?"
    target = 60
    answer = True

    def setup(self, rng, ctx):
        need, kw, cmd = rng.choice(APROPOS_POOL)
        prompt = (f"You need a command that {need}, and you don't know its name. `man -k` "
                  f"searches the one-line description of every manual on the system. Search "
                  f"for a word that would be in that description.\n\nSend the command's name.")
        return {"cmd": cmd, "kw": kw, "prompt": prompt}

    def check(self, st, ctx, cwd, answer):
        a = (answer or "").strip().split(" ")[0]
        if a == st["cmd"]:
            return Result(True)
        return Result(False, f"Not {a or 'that'}. Read each result's description: which one {self._need(st)}?")

    def _need(self, st):
        for need, kw, cmd in APROPOS_POOL:
            if cmd == st["cmd"]:
                return need
        return "does it"

    def hint(self, st, ctx):
        return f"Try:\n\n    `man -k '{st['kw']}'`\n\nThen read the descriptions on the right."


class Synopsis(Exercise):
    id = "help.synopsis"
    title = "Decode a SYNOPSIS"
    target = 60
    answer = True

    def setup(self, rng, ctx):
        cmd, line, elems = rng.choice(SYNOPSES)
        qs = []
        for name, optional, repeatable in elems:
            qs.append((f"Can you leave out {name} entirely?", optional))
            qs.append((f"Can you give more than one {name}?", repeatable))
        qs.append(("Can you give more than one OPTION?", True))
        qs = rng.sample(qs, 3)
        lines = "\n".join(f"    {i + 1}. {q}" for i, (q, _) in enumerate(qs))
        prompt = (f"Here's the SYNOPSIS line from `man {cmd}`:\n\n    {line}\n\n"
                  f"According to this line, answer y or n, in order:\n\n{lines}\n\n"
                  f"For example: `drill answer y n y`")
        return {"cmd": cmd, "line": line, "answers": ["y" if a else "n" for _, a in qs], "prompt": prompt}

    def check(self, st, ctx, cwd, answer):
        got = [w[0].lower() for w in (answer or "").replace(",", " ").split()]
        if len(got) != len(st["answers"]):
            return Result(False, f"Send {len(st['answers'])} answers, one per question, like: y n y")
        wrong = [str(i + 1) for i, (g, a) in enumerate(zip(got, st["answers"])) if g != a]
        if not wrong:
            return Result(True)
        return Result(False, f"Question {', '.join(wrong)} {'is' if len(wrong) == 1 else 'are'} wrong.")

    def hint(self, st, ctx):
        return ("    [FILE]     square brackets: optional, you can leave it out\n"
                "    FILE...    three dots: you can give more than one\n"
                "    FILE       neither: required, and exactly one")


class TldrTar(Exercise):
    id = "help.tldr"
    title = "Learn it from examples"
    target = 90

    def setup(self, rng, ctx):
        game = rng.choice(world.GAMES)
        inner = f"{game}-{rng.choice(['levels', 'maps', 'mods', 'soundtrack'])}"
        ext = rng.choice(["gz", "xz", "bz2"])
        name = f"{inner}.tar.{ext}"
        files = {f"{inner}/part-{i:02d}.dat": world.filler(rng) for i in range(1, rng.randint(4, 7))}
        dl = ctx.lab / "Downloads"
        dl.mkdir(parents=True)
        with tarfile.open(dl / name, f"w:{ext}") as tar:
            for path, text in files.items():
                data = text.encode()
                info = tarfile.TarInfo(path)
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))
        prompt = (f"A friend sent you `{name}` and it's in `{ctx.show(dl)}`. You've never "
                  f"unpacked one of these. `tldr` shows a command's most common uses as "
                  f"short examples. Use it to work out how, then unpack the archive right "
                  f"there in Downloads.")
        return {"name": name, "inner": inner, "files": files, "dl": str(dl), "prompt": prompt}

    def check(self, st, ctx, cwd, answer):
        dl = ctx.resolve(st["dl"])
        if all((dl / p).is_file() and (dl / p).read_text() == t for p, t in st["files"].items()):
            return Result(True, "tar figures out the compression on its own when it extracts.")
        found = [p for p in ctx.home.rglob(st["inner"]) if p.is_dir() and p.parent != dl]
        if found:
            return Result(False, f"You unpacked it into {ctx.show(found[0].parent)}. tar extracts into "
                                 f"the folder you're in: cd to Downloads first.")
        return Result(False, f"I don't see {st['inner']}/ in {ctx.show(dl)} yet.")

    def hint(self, st, ctx):
        return (f"`tldr tar` and look for the line that starts with E[x]tract. Then:\n\n"
                f"    `cd {ctx.show(ctx.resolve(st['dl']))}`\n    `tar xf {st['name']}`")


LESSON = Lesson(
    number=0,
    name="Help yourself",
    hook="You'll never memorize everything. You'll learn to look it up fast.",
    intro=INTRO,
    exercises=[HelpFlag(), ManFlag(), Apropos(), Synopsis(), TldrTar()],
)
