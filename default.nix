with import <nixpkgs> {};
mkShell {
  nativeBuildInputs = [
    bashInteractive
    hugo
    calibre
    pandoc
    python3Packages.python-frontmatter
    # also fixed by https://github.com/NixOS/nixpkgs/pull/117904
    python3Packages.cchardet
  ];
}
