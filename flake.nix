{
  description = "My Python development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
  };

  outputs = { self, nixpkgs }: {
    devShell = nixpkgs.mkShell {
      buildInputs = with nixpkgs; [
        poetry
        python3_12
      ];

      shellHook = ''
        export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
        poetry env use $(which python3.12)
        source $(poetry env info --path)/bin/activate
      '';
    };
  };
}
