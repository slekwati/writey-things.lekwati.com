with import <nixpkgs> {};
mkShell {
  nativeBuildInputs = [
    bashInteractive
    hugo
    calibre
    python3Packages.python-frontmatter
  ];
}
