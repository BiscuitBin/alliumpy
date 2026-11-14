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
      # The parity reference: upstream's allium-cli at the version the
      # allium-parser pin names. `just version-check` reads this line and fails
      # when it differs from the pin, so an upstream bump moves it, and the
      # source and vendor hashes below, in the same change
      # (docs/how-to/bump-upstream.md).
      alliumCliVersion = "3.6.1";

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
            (biscuitGamesTooling ps)
          ]);
          # The `bg-*` commands, `just check`'s runner among them, from the same
          # revision the pixi manifest names (tag v0.3.0); a bump moves both in one
          # change until pixi is removed. The package has no
          # dependencies. Its build backend asks for uv_build below 0.12, which
          # nixpkgs has moved past; the backend's output for this layout does not
          # depend on that bound, so the bound is relaxed here and nowhere else.
          biscuitGamesTooling =
            ps:
            ps.buildPythonPackage {
              pname = "biscuit-games-tooling";
              version = "0.3.0";
              pyproject = true;
              src = pkgs.fetchFromGitHub {
                owner = "steven-cutting";
                repo = "biscuit_games_tooling";
                rev = "6c5c07f6bec86e86b3930dfa41392e4b440e8c85";
                hash = "sha256-iHgEOv3KnCpSNO4/jLyc9jJqcl1pP+zoVsqyMlxuMvk=";
              };
              postPatch = ''
                substituteInPlace pyproject.toml \
                  --replace-fail 'requires = ["uv_build>=0.11,<0.12"]' 'requires = ["uv_build"]'
              '';
              build-system = [ ps.uv-build ];
              pythonImportsCheck = [ "biscuit_games_tooling" ];
            };
          # nixpkgs does not carry rustqual, so it is built here from the crate
          # crates.io publishes, with the crate's own lockfile and the pinned
          # toolchain. This version is the one the metrics gate requires.
          rustPlatform = pkgs.makeRustPlatform {
            cargo = rustToolchain;
            rustc = rustToolchain;
          };
          # Upstream's own command, built from the crate crates.io publishes with
          # the crate's own Cargo.lock, so the comparison is with exactly what
          # upstream ships. It never goes on PATH: the wheel's console script has
          # the same name. The shell exports where it is instead.
          parityReference = rustPlatform.buildRustPackage (finalAttrs: {
            pname = "allium-cli";
            version = alliumCliVersion;
            src = pkgs.fetchCrate {
              inherit (finalAttrs) pname version;
              hash = "sha256-jKrGgHowbTmZBrTKxWMpVT23GiZzz9xMk2f18FLvBHg=";
            };
            cargoHash = "sha256-KEOJXDhEdlLoGLQ710H8rFf8NxQ1AvS7vgIJRDMWHR0=";
            doCheck = false;
          });
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
              # The hook runner and every tool its Nix-form configuration calls
              # by name, so installing the hooks fetches nothing.
              pkgs.prek
              pkgs.editorconfig-checker
              pkgs.markdownlint-cli2
              pkgs.typos
              pkgs.lychee
              pkgs.shellcheck
              pkgs.actionlint
              pkgs.ripsecrets
              pkgs.nixfmt
              pkgs.statix
              pkgs.deadnix
            ]
            ++ pkgs.lib.optionals pkgs.stdenv.hostPlatform.isDarwin [ pkgs.libiconv ];

            # The Justfile reads this to know the shell, not pixi, provides the tools.
            ALLIUMPY_TOOLS = "nix";
            # The metrics gate refuses a rustqual of any other version.
            ALLIUMPY_RUSTQUAL_VERSION = rustqual.version;
            ALLIUMPY_PARITY_REFERENCE = "${parityReference}/bin/allium";
          };
        }
      );
    };
}
