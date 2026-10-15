from .. import world
from ..engine import Exercise, Lesson, Result

INTRO = """
Downloads fills up. Projects need folders. Saves need backups. A file manager makes you
drag things one at a time; the terminal does a hundred files in one line.

    `mkdir -p a/b/c`       make folders, including any missing ones in between
    `cp file copy`         copy                `cp -r folder copy`   copy a whole folder
    `mv file there/`       move                `mv old new`          rename (same command)
    `rm file`              delete              `rm -r folder`        delete a folder and everything in it

Wildcards pick many files at once. The shell expands them before the command runs:

    `*.png`       every name ending in .png
    `*`           everything (except hidden files)
    `report-?.pdf`  ? is exactly one character

There's no trash can. rm is permanent, so before you delete with a wildcard, run `ls`
with the same pattern first and look at what it matches.
"""

IMAGE = ["jpg", "png"]
OTHER = ["deb", "mp3", "zip", "txt", "mp4"]


class MakeTree(Exercise):
    id = "files.tree"
    title = "Set up a project"
    target = 45

    def setup(self, rng, ctx):
        name = rng.choice(world.GAMES) + "-" + rng.choice(["mod", "remake", "jam", "demo"])
        nested = rng.sample(["assets/sprites", "assets/sounds", "assets/maps", "docs/notes", "src/ui"], 2)
        flat = rng.sample(["docs", "build", "saves", "config", "levels", "tests"], 2)
        wanted = sorted(set(nested + flat))
        root = ctx.lab / "projects" / name
        listing = "\n".join(f"    {w}/" for w in wanted)
        prompt = (f"You're starting a new project called {name}. Create its folder at "
                  f"`{ctx.show(root)}` with these folders inside it:\n\n{listing}")
        return {"root": str(root), "wanted": wanted, "prompt": prompt}

    def check(self, st, ctx, cwd, answer):
        root = ctx.resolve(st["root"])
        missing = [w for w in st["wanted"] if not (root / w).is_dir()]
        if not missing:
            return Result(True)
        return Result(False, f"Still missing: {', '.join(missing)}")

    def hint(self, st, ctx):
        r = ctx.show(ctx.resolve(st["root"]))
        return (f"mkdir takes several names at once, and -p creates the parents too:\n\n"
                f"    `mkdir -p {r}/{st['wanted'][0]} {r}/{st['wanted'][1]} ...`")


class SortDownloads(Exercise):
    id = "files.sort"
    title = "Clean up Downloads"
    target = 60

    def setup(self, rng, ctx):
        dl, pics, docs = ctx.lab / "Downloads", ctx.lab / "Pictures", ctx.lab / "Documents"
        for d in (dl, pics, docs):
            d.mkdir(parents=True)
        names = set()

        def fresh(ext):
            while True:
                n = f"{rng.choice(world.WORDS)}-{rng.randint(1, 99)}.{ext}"
                if n not in names:
                    names.add(n)
                    return n

        images = [fresh(rng.choice(IMAGE)) for _ in range(rng.randint(3, 5))]
        pdfs = [fresh("pdf") for _ in range(rng.randint(2, 4))]
        others = [fresh(rng.choice(OTHER)) for _ in range(rng.randint(3, 5))]
        content = {}
        for n in images + pdfs + others:
            content[n] = world.filler(rng)
            world.touch(dl / n, content[n])
        prompt = (f"`{ctx.show(dl)}` is a mess. Move every image (.jpg and .png) into "
                  f"`{ctx.show(pics)}` and every PDF into `{ctx.show(docs)}`. Leave everything "
                  f"else where it is.")
        return {"dl": str(dl), "pics": str(pics), "docs": str(docs), "images": images,
                "pdfs": pdfs, "others": others, "content": content, "prompt": prompt}

    def check(self, st, ctx, cwd, answer):
        dl, pics, docs = (ctx.resolve(st[k]) for k in ("dl", "pics", "docs"))
        problems = []
        for group, dest in ((st["images"], pics), (st["pdfs"], docs), (st["others"], dl)):
            for n in group:
                p = dest / n
                if not p.is_file() or p.read_text() != st["content"][n]:
                    problems.append(f"{n} should be in {ctx.show(dest)}")
        if not problems:
            return Result(True)
        more = f" (and {len(problems) - 3} more)" if len(problems) > 3 else ""
        return Result(False, "; ".join(problems[:3]) + more)

    def hint(self, st, ctx):
        dl = ctx.show(ctx.resolve(st["dl"]))
        return (f"mv takes many files and puts them in the last argument:\n\n"
                f"    `mv {dl}/*.jpg {dl}/*.png {ctx.show(ctx.resolve(st['pics']))}/`\n\n"
                f"If there are no .jpg files, *.jpg matches nothing and mv complains. "
                f"`ls {dl}` first.")


class Backup(Exercise):
    id = "files.backup"
    title = "Back it up first"
    target = 25

    def setup(self, rng, ctx):
        roots, dirs = world.world(rng, ctx.lab, games=2)
        file = rng.choice([p for p in ctx.lab.rglob("*") if p.is_file() and p.suffix in (".ini", ".toml", ".dat")])
        prompt = (f"You're about to edit `{ctx.show(file)}`. If you break it, the game won't "
                  f"start. Make a copy next to it called `{file.name}.bak` first.")
        return {"file": str(file), "text": file.read_text(), "prompt": prompt}

    def check(self, st, ctx, cwd, answer):
        f = ctx.resolve(st["file"])
        bak = f.with_name(f.name + ".bak")
        if not f.is_file():
            return Result(False, f"{f.name} is gone. That was a move, not a copy.")
        if not bak.is_file():
            return Result(False, f"I don't see {ctx.show(bak)}.")
        if bak.read_text() != st["text"]:
            return Result(False, f"{bak.name} doesn't match the original.")
        return Result(True)

    def hint(self, st, ctx):
        f = ctx.show(ctx.resolve(st["file"]))
        return f"`cp {f} {f}.bak`"


class DeleteMatching(Exercise):
    id = "files.delete"
    title = "Delete only the junk"
    target = 40

    def setup(self, rng, ctx):
        build = ctx.lab / "build"
        build.mkdir(parents=True)
        junk = sorted({f"{rng.choice(world.WORDS)}-{rng.randint(100, 999)}.tmp" for _ in range(rng.randint(4, 7))})
        # Always two decoys with "tmp" in the name, so a sloppy *tmp* wildcard costs you.
        keep = rng.sample(["notes.tmp.txt", "tmp-plan.md", "old.tmp.bak", "tmpfile-list.txt"], 2) \
            + rng.sample(["game.bin", "cache.temp", f"{rng.choice(world.WORDS)}.log", "README.md"], 2)
        for n in junk + keep:
            world.touch(build / n, world.filler(rng))
        prompt = (f"`{ctx.show(build)}` is full of leftover .tmp files from the last build. "
                  f"Delete every file whose name ends in .tmp, and nothing else.")
        return {"dir": str(build), "junk": junk, "keep": keep, "prompt": prompt}

    def check(self, st, ctx, cwd, answer):
        d = ctx.resolve(st["dir"])
        left = [n for n in st["junk"] if (d / n).exists()]
        lost = [n for n in st["keep"] if not (d / n).exists()]
        if lost:
            return Result(False, f"You deleted {', '.join(lost)}, which doesn't end in .tmp.")
        if left:
            return Result(False, f"{len(left)} .tmp file{'s are' if len(left) > 1 else ' is'} still there.")
        return Result(True)

    def hint(self, st, ctx):
        d = ctx.show(ctx.resolve(st["dir"]))
        return f"Look before you delete:\n\n    `ls {d}/*.tmp`\n    `rm {d}/*.tmp`"


class MoveRename(Exercise):
    id = "files.moverename"
    title = "Move and rename at once"
    target = 30

    def setup(self, rng, ctx):
        dl, docs = ctx.lab / "Downloads", ctx.lab / "Documents"
        docs.mkdir(parents=True)
        src = rng.choice(["report.pdf", "invoice.pdf", "manual.pdf", "receipt.pdf", "itinerary.pdf"])
        new = f"{rng.randint(2019, 2026)}-{rng.choice(['q1', 'q2', 'q3', 'q4', 'march', 'june'])}-{src}"
        text = world.filler(rng)
        world.touch(dl / src, text)
        prompt = (f"`{src}` landed in `{ctx.show(dl)}`. It belongs in `{ctx.show(docs)}`, and "
                  f"it should be named `{new}` there. Do it with one command.")
        return {"src": str(dl / src), "dest": str(docs / new), "text": text, "prompt": prompt}

    def check(self, st, ctx, cwd, answer):
        src, dest = ctx.resolve(st["src"]), ctx.resolve(st["dest"])
        if not dest.is_file() or dest.read_text() != st["text"]:
            return Result(False, f"I don't see it at {ctx.show(dest)}.")
        if src.exists():
            return Result(False, f"The original is still in {ctx.show(src.parent)}. That was a copy, not a move.")
        return Result(True)

    def hint(self, st, ctx):
        return (f"mv moves and renames in one go when you give it the new name:\n\n"
                f"    `mv {ctx.show(ctx.resolve(st['src']))} {ctx.show(ctx.resolve(st['dest']))}`")


class CopyDir(Exercise):
    id = "files.copydir"
    title = "Back up a whole folder"
    target = 30

    def setup(self, rng, ctx):
        roots, dirs = world.world(rng, ctx.lab, games=2)
        game = rng.choice(roots)
        saves = game / "saves"
        backup = game / "saves-backup"
        prompt = (f"There's a patch for {game.name} tonight, and patches have eaten saves "
                  f"before. Copy `{ctx.show(saves)}` and everything in it to "
                  f"`{ctx.show(backup)}`.")
        return {"saves": str(saves), "backup": str(backup), "snap": world.snapshot(saves), "prompt": prompt}

    def check(self, st, ctx, cwd, answer):
        saves, backup = ctx.resolve(st["saves"]), ctx.resolve(st["backup"])
        if not world.matches(saves, st["snap"]):
            return Result(False, "The original saves folder changed. Copy it, don't move it.")
        if not backup.is_dir():
            return Result(False, f"I don't see {ctx.show(backup)}.")
        if (backup / "saves").is_dir():
            return Result(False, f"The copy ended up inside {ctx.show(backup)}/saves. Delete the backup "
                                 f"and copy again: when the destination already exists, cp puts the "
                                 f"folder inside it.")
        if not world.matches(backup, st["snap"]):
            return Result(False, "The backup doesn't have everything the original has.")
        return Result(True)

    def hint(self, st, ctx):
        return (f"Plain cp skips folders. -r copies recursively:\n\n"
                f"    `cp -r {ctx.show(ctx.resolve(st['saves']))} {ctx.show(ctx.resolve(st['backup']))}`")


class RemoveDir(Exercise):
    id = "files.removedir"
    title = "Delete a whole folder"
    target = 25

    def setup(self, rng, ctx):
        roots, dirs = world.world(rng, ctx.lab, games=2)
        game = rng.choice(roots)
        old = game / f"build-{rng.randint(1, 4)}.{rng.randint(0, 9)}"
        for i in range(rng.randint(3, 6)):
            world.touch(old / rng.choice(["bin", "obj", "pkg"]) / f"part{i}.o", world.filler(rng))
        keep = {str(p.relative_to(game)): p.read_text() for p in game.rglob("*")
                if p.is_file() and old not in p.parents}
        prompt = (f"`{ctx.show(old)}` is three versions out of date and taking up space. "
                  f"Delete it and everything inside it. Keep the rest of {game.name}.")
        return {"game": str(game), "old": str(old), "keep": keep, "prompt": prompt}

    def check(self, st, ctx, cwd, answer):
        game, old = ctx.resolve(st["game"]), ctx.resolve(st["old"])
        lost = [k for k in st["keep"] if not (game / k).is_file()]
        if lost:
            return Result(False, f"You deleted more than the old build: {lost[0]} is gone too.")
        if old.exists():
            return Result(False, f"{ctx.show(old)} is still there.")
        return Result(True)

    def hint(self, st, ctx):
        return (f"rm on its own won't remove a folder. -r removes it and everything inside:\n\n"
                f"    `rm -r {ctx.show(ctx.resolve(st['old']))}`")


LESSON = Lesson(
    number=2,
    name="Move things around",
    hook="Clean up the mess in Downloads.",
    intro=INTRO,
    exercises=[MakeTree(), SortDownloads(), Backup(), DeleteMatching(), MoveRename(), CopyDir(), RemoveDir()],
)
