#!/usr/bin/env python3

import subprocess
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
import argparse
import os
import uuid
import hashlib
import sys
from typing import Dict

import frontmatter


ROOT = Path(__file__).parent.resolve()


@dataclass
class Options:
    source_dir: Path
    output_dir: Path
    cover_dir: Path


def parse_args() -> Options:
    parser = argparse.ArgumentParser()
    help = "File to import rather than default.nix. Examples, ./release.nix"
    parser.add_argument("source_dir", default="./.")
    parser.add_argument("--covers", default="./.")
    parser.add_argument("-o", "--output", default="./.")
    args = parser.parse_args()
    return Options(
        source_dir=Path(args.source_dir),
        cover_dir=Path(args.covers),
        output_dir=Path(args.output)
    )

def set_default(metadata: Dict[str, str], key: str, value: str):
    metadata[key] = metadata.get(key, value)

def sha256sum(filename: str) -> str:
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()

def convert_epub(source: Path, target: Path, cover_dir: Path) -> bool:
    post = frontmatter.load(source)
    set_default(post, "creator", "Shannan Lekwati")
    set_default(post, "lang", "en")
    date = post.get("date")
    urn = uuid.uuid3(uuid.NAMESPACE_URL, 'blog.lekwati.com/ebooks/{target.name}').urn
    post["identifier"] = urn
    if date:
        post["date"] = post["date"].replace(tzinfo=None)
    post.get("creator", "Shannan Lekwati")
    summary = post.get("summary")
    if summary:
        set_default(post, "description", summary)

    post["titlepage"] = False
    cover_image = post.get("cover", {}).get("image")
    if cover_image:
        cover_path = cover_dir.joinpath(cover_image)
        if cover_path.exists():
            post["cover-image"] = str(cover_path)
        else:
            print(f"WARNING: {cover_image} in {source} does not exists", file=sys.stderr)

    with NamedTemporaryFile(suffix=source.suffix) as f:
        frontmatter.dump(post, f)
        f.flush()
        print(f"write {target}")
        template = ROOT.joinpath("epub.html")
        # pandoc put dates into document
        env = os.environ.copy()
        libfaketime = env.get("LIBFAKETIME")
        if libfaketime:
            env.update(FAKETIME="2000-01-01 11:12:13",
                       LD_PRELOAD=libfaketime,
                       TZ="UTC")
        subprocess.run(["pandoc", f.name, "-o", target, "--template", template],
                       env=env)


def convert_mobi(source: Path, target: Path) -> None:
    subprocess.run(["ebook-convert", source, target])


def main() -> None:
    opts = parse_args()

    for subdir_str, dirs, files in os.walk(opts.source_dir):
        subdir = Path(subdir_str)
        for file in files:
            target = opts.output_dir.joinpath(Path(file).stem + ".epub")
            if target.exists():
                hashsum = sha256sum(str(target))
            else:
                hashsum = ""
            convert_epub(subdir.joinpath(file), target, opts.cover_dir)
            mobi = opts.output_dir.joinpath(Path(file).stem + ".mobi")
            if hashsum != "":
                new_hashsum = sha256sum(str(target))
                if hashsum != new_hashsum:
                    # convert-ebook is not reproducible, but pandoc is with our faketime hack.
                    # Therefore only rebuild mobi if epub has changed
                    convert_mobi(target, mobi)



if __name__ == "__main__":
    main()
