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
  LIBFAKETIME = "${libfaketime}/lib/libfaketime.so.1";
}
