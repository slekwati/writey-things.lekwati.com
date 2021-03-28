with import <nixpkgs> {};
mkShell {
  nativeBuildInputs = [
    bashInteractive
    hugo
    calibre
    pandoc
    python3Packages.python-frontmatter
  ];
}
