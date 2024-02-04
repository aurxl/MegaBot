{ pkgs ? import <nixpkgs> {} }:
  pkgs.mkShell {
    buildInputs = with pkgs; [
      poetry
      python311
      python311Packages.virtualenv
    ];

  shellHook = ''
    export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
  '';
}
