{ pkgs ? import <nixpkgs> {} }:
  pkgs.mkShell {
    buildInputs = with pkgs; [
      poetry
      python312
    ];

  shellHook = ''
    export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
    poetry env use $(which python)
    source $(poetry env info --path)/bin/activate
  '';
}
