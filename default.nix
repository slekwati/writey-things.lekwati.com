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
  LD_PRELOAD = "${libfaketime}/lib/libfaketime.so.1";
  # pandoc put dates into document
  FAKETIME = "2000-01-01 11:12:13";
}
