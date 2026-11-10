{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
    buildInputs = with pkgs; [
      (python314.withPackages (python-pkgs: with python-pkgs; [
        click
        flask
        pwdlib
        weasyprint
      ]))
      sqlite
      uv
    ];
}

