{
  description = "alliumpy: every tool the gates run with, from one pinned source";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    rust-overlay = {
      url = "github:oxalica/rust-overlay";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      nixpkgs,
      rust-overlay,
      ...
    }:
    let
      # Apple silicon macOS and x86-64 Linux are where contributors and CI work.
      # arm64 Linux lets the same shell run natively in a Linux container on an
      # Apple silicon Mac.
      systems = [
        "aarch64-darwin"
        "x86_64-linux"
        "aarch64-linux"
      ];
      forEachSystem =
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
    in
    {
      formatter = forEachSystem (pkgs: pkgs.nixfmt-tree);

      devShells = forEachSystem (
        pkgs:
        let
          # rust-toolchain.toml stays the single owner of the Rust version and
          # its components; nixpkgs decides every other tool's version.
          rustToolchain = pkgs.rust-bin.fromRustupToolchainFile ./rust-toolchain.toml;
        in
        {
          # mkShell, not mkShellNoCC: cargo links through the C compiler, and
          # libfuzzer-sys's build script compiles C++ whenever the fuzz crate builds.
          default = pkgs.mkShell {
            packages = [
              rustToolchain
              pkgs.just
              pkgs.cargo-nextest
              pkgs.python314
              pkgs.nixfmt
              pkgs.statix
              pkgs.deadnix
            ]
            ++ pkgs.lib.optionals pkgs.stdenv.hostPlatform.isDarwin [ pkgs.libiconv ];

            # The Justfile reads this to know the shell, not pixi, provides the tools.
            ALLIUMPY_TOOLS = "nix";
          };
        }
      );
    };
}
