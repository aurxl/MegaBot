{
  description = "My Python development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
  };

  outputs = { self, nixpkgs }: let
    pkgs = nixpkgs.legacyPackages.x86_64-linux;
  in {
    devShell.x86_64-linux = pkgs.mkShell {
      buildInputs = with pkgs; [
        poetry
        python312

        libopus
        ffmpeg_6
      ];

      shellHook = ''
        if [ "$TERM_PROGRAM" != "vscode" ]; then
          poetry env use $(which python3.12)
          source $(poetry env info --path)/bin/activate
        fi
        export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
      '';
    };
  };
}
