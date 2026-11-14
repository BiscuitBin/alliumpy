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
          # One interpreter for pyo3's build script, pytest, mypy and stubtest.
          # mypy comes from this Python's own package set, not nixpkgs' top-level
          # application, so that stubtest imports the extension under the
          # interpreter that built it.
          python = pkgs.python314.withPackages (ps: [
            ps.pytest
            ps.mypy
          ]);
          # nixpkgs does not carry rustqual, so it is built here from the crate
          # crates.io publishes, with the crate's own lockfile and the pinned
          # toolchain. This version is the one the metrics gate requires.
          rustPlatform = pkgs.makeRustPlatform {
            cargo = rustToolchain;
            rustc = rustToolchain;
          };
          rustqual = rustPlatform.buildRustPackage (finalAttrs: {
            pname = "rustqual";
            version = "1.8.3";
            src = pkgs.fetchCrate {
              inherit (finalAttrs) pname version;
              hash = "sha256-xplBYaftBxCRwNZwyoHU68vPi1ooQ2krckwi0RoJ0pM=";
            };
            cargoHash = "sha256-oz6R8k7NoE2Gf51N7ZCFaPU+ij/AL315qFzdMz6hCh4=";
            doCheck = false;
          });
        in
        {
          # mkShell, not mkShellNoCC: cargo links through the C compiler, and
          # libfuzzer-sys's build script compiles C++ whenever the fuzz crate builds.
          default = pkgs.mkShell {
            packages = [
              rustToolchain
              pkgs.just
              pkgs.cargo-nextest
              python
              pkgs.maturin
              pkgs.uv
              pkgs.ruff
              pkgs.cargo-hack
              pkgs.cargo-llvm-cov
              pkgs.cargo-deny
              pkgs.cargo-shear
              pkgs.cargo-insta
              pkgs.cargo-fuzz
              pkgs.cargo-mutants
              pkgs.taplo
              rustqual
              pkgs.nixfmt
              pkgs.statix
              pkgs.deadnix
            ]
            ++ pkgs.lib.optionals pkgs.stdenv.hostPlatform.isDarwin [ pkgs.libiconv ];

            # The Justfile reads this to know the shell, not pixi, provides the tools.
            ALLIUMPY_TOOLS = "nix";
            # The metrics gate refuses a rustqual of any other version.
            ALLIUMPY_RUSTQUAL_VERSION = rustqual.version;
          };
        }
      );
    };
}
