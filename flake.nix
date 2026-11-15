{
  description = "alliumpy's development environment: the Rust toolchain rust-toolchain.toml names, Python, and every tool a recipe or hook calls (decision 0018)";

  # One pin for everything: flake.lock. `just lock` adds an input flake.nix newly names
  # and moves nothing else; `just lock-upgrade` moves every input to the head of the ref
  # below. The URLs avoid GitHub's archive API, which is rate-limited without a token:
  # nixpkgs comes from the channel (a Hydra-tested revision that cache.nixos.org has
  # already built for both systems), the others over git.
  inputs = {
    # Named `nixpkgs` on purpose: `nix develop` takes its bash from the input of that name.
    nixpkgs.url = "https://channels.nixos.org/nixpkgs-unstable/nixexprs.tar.xz";
    rust-overlay = {
      url = "git+https://github.com/oxalica/rust-overlay?shallow=1";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    # The shared checkers (decision 0002) at a release tag; nix/biscuit-games-tooling.nix
    # builds them. A new tag is an edit to this line, then `just lock`.
    biscuit-games-tooling = {
      url = "git+https://github.com/steven-cutting/biscuit_games_tooling?ref=refs/tags/v0.3.0&shallow=1";
      flake = false;
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      rust-overlay,
      biscuit-games-tooling,
    }:
    let
      # The two platforms with evidence: CI's Linux and the maintainer's Apple silicon
      # (macos-smoke). Another joins when a run on it is shown.
      systems = [
        "x86_64-linux"
        "aarch64-darwin"
      ];
      perSystem =
        f:
        nixpkgs.lib.genAttrs systems (
          system:
          f (
            import nixpkgs {
              inherit system;
              overlays = [ rust-overlay.overlays.default ];
            }
          )
        );
      shellFor =
        pkgs:
        import ./nix/dev-shell.nix {
          inherit pkgs;
          inputs = { inherit nixpkgs rust-overlay biscuit-games-tooling; };
        };
    in
    {
      devShells = perSystem (pkgs: {
        default = shellFor pkgs;
      });
      # The same derivation as a package, so `just sync` can record it as a GC root.
      packages = perSystem (pkgs: {
        dev-shell = shellFor pkgs;
      });
      # The Justfile owns every check; this one makes `nix flake check` build the shell.
      checks = perSystem (pkgs: {
        dev-shell = shellFor pkgs;
      });
      formatter = perSystem (pkgs: pkgs.nixfmt-tree);
    };
}
