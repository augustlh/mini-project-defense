{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
    buildInputs = with pkgs; [
      (python314.withPackages (python-pkgs: with python-pkgs; [
        click
        flask
        argon2-cffi-bindings
      ]))
      sqlite
      libargon2
      uv
    ];
}

