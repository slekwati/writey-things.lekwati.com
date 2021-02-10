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
from typing import Dict, List

from calibre.utils.logging import Log
from calibre.customize.conversion import OptionRecommendation
from calibre.ebooks.conversion.plumber import Plumber
from calibre.ebooks.conversion.plugins.mobi_output import MOBIOutput
from calibre.ebooks.conversion.plugins.epub_output import EPUBOutput

import frontmatter


ROOT = Path(__file__).parent.resolve()


@dataclass
class Options:
    source_files: List[Path]
    output_dir: Path
    cover_dir: Path


def parse_args() -> Options:
    parser = argparse.ArgumentParser()
    help = "File to import rather than default.nix. Examples, ./release.nix"
    parser.add_argument("source_files", nargs="+", default="./.")
    parser.add_argument("--covers", default="./.")
    parser.add_argument("-o", "--output", default="./.")
    args = parser.parse_args()
    return Options(
        source_files=[Path(s) for s in args.source_files],
        cover_dir=Path(args.covers),
        output_dir=Path(args.output)
    )


def convert_document(source: Path, target: Path, cover_dir: Path):
    post = frontmatter.load(source)
    log = Log()

    title = post.get("title", "unknown title")
    author = post.get("creator", "Shannan Lekwati")

    args = [
        ("authors", author),
        ("language", post.get("lang", "en")),
        ("title", title),
    ]

    date = post.get("date")
    if date:
        args += [
            ("pubdate", str(post["date"])),
            ("timestamp", str(post["date"]))
        ]

    summary = post.get("summary")
    if summary:
        args += [ ("comments", summary) ]

    cover_image = post.get("cover", {}).get("image")
    if cover_image:
        cover_path = cover_dir.joinpath(cover_image).absolute()
        if cover_path.exists():
            args += [ ("cover", str(cover_path)) ]
        else:
            print(f"WARNING: {cover_image} in {source} does not exists", file=sys.stderr)

    with NamedTemporaryFile(suffix=source.suffix, mode="w") as f:
        f.write(f"# {title}\n")
        f.write(f"** by {author} **\n\n")
        f.write(post.content)
        f.flush()

        plumber = Plumber(f.name, target, log)
        recommendations = [(k, v, OptionRecommendation.HIGH) for (k,v) in args]
        plumber.merge_ui_recommendations(recommendations)
        plumber.run()


def main() -> None:
    opts = parse_args()

    for source_file in opts.source_files:
        target = opts.output_dir.joinpath(source_file.stem + ".epub")
        convert_document(source_file, target, opts.cover_dir)
        target = opts.output_dir.joinpath(source_file.stem + ".mobi")
        convert_document(source_file, target, opts.cover_dir)



if __name__ == "__main__":
    main()
