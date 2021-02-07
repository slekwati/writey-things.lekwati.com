with import <nixpkgs> {};
mkShell {
  nativeBuildInputs = [
    bashInteractive
    hugo
    pandoc
    calibre
    (python3.withPackages (ps: [
      ps.python-frontmatter
    ]))
  ];
}
