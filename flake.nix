{
  description = "alliumpy: every tool the gates run with, from one pinned source";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    rust-overlay = {
      url = "github:oxalica/rust-overlay";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    # Builds the crates and the wheel in the sandbox from Cargo.lock, with the
    # dependencies as a derivation of their own.
    crane.url = "github:ipetkov/crane";
  };

  outputs =
    {
      nixpkgs,
      rust-overlay,
      crane,
      ...
    }:
    let
      # The parity reference: upstream's allium-cli at the version the
      # allium-parser pin names. `just version-check` reads this line and fails
      # when it differs from the pin, so an upstream bump moves it, and the
      # source and vendor hashes below, in the same change
      # (docs/how-to/bump-upstream.md).
      alliumCliVersion = "3.6.1";
      # The rustqual the metrics gate requires; `just metrics` reads this line.
      rustqualVersion = "1.8.3";

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

      # Everything one system needs, shared by the dev shell and the packages.
      build =
        pkgs:
        let
          inherit (pkgs) lib;

          # rust-toolchain.toml stays the single owner of the Rust version and
          # its components; nixpkgs decides every other tool's version.
          rustToolchain = pkgs.rust-bin.fromRustupToolchainFile ./rust-toolchain.toml;
          rustPlatform = pkgs.makeRustPlatform {
            cargo = rustToolchain;
            rustc = rustToolchain;
          };

          # The `bg-*` commands, `just check`'s runner among them, at the
          # revision tag v0.3.0 names. The package has no dependencies. Its
          # build backend asks for uv_build below 0.12, which nixpkgs has moved
          # past; the backend's output for this layout does not depend on that
          # bound, so the bound is relaxed here and nowhere else.
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

          # One interpreter for pyo3's build script, pytest, mypy and stubtest.
          # mypy comes from this Python's own package set, not nixpkgs' top-level
          # application, so that stubtest imports the extension under the
          # interpreter that built it.
          python = pkgs.python314.withPackages (ps: [
            ps.pytest
            ps.mypy
            (biscuitGamesTooling ps)
          ]);

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

          # nixpkgs does not carry rustqual, so it is built here from the crate
          # crates.io publishes, with the crate's own lockfile and the pinned
          # toolchain. This version is the one the metrics gate requires.
          rustqual = rustPlatform.buildRustPackage (finalAttrs: {
            pname = "rustqual";
            version = rustqualVersion;
            src = pkgs.fetchCrate {
              inherit (finalAttrs) pname version;
              hash = "sha256-xplBYaftBxCRwNZwyoHU68vPi1ooQ2krckwi0RoJ0pM=";
            };
            cargoHash = "sha256-oz6R8k7NoE2Gf51N7ZCFaPU+ij/AL315qFzdMz6hCh4=";
            doCheck = false;
          });

          # The crates and the wheel, built in the sandbox. A flake sees only
          # what Git tracks, and the build sees only these paths of it, so an
          # edit elsewhere does not rebuild it.
          craneLib = (crane.mkLib pkgs).overrideToolchain (_: rustToolchain);
          src = lib.fileset.toSource {
            root = ./.;
            fileset = lib.fileset.unions [
              ./Cargo.toml
              ./Cargo.lock
              ./rust-toolchain.toml
              ./clippy.toml
              ./rustfmt.toml
              ./.config/nextest.toml
              ./crates
              ./tests/fixtures
            ];
          };
          workspaceVersion = (builtins.fromTOML (builtins.readFile ./Cargo.toml)).workspace.package.version;
          # A plain interpreter for pyo3's build script: the wheel is abi3, so
          # nothing but its version and headers matter.
          buildPython = pkgs.python314;
          commonArgs = {
            inherit src;
            pname = "alliumpy";
            version = workspaceVersion;
            strictDeps = true;
            nativeBuildInputs = [ buildPython ];
            buildInputs = lib.optionals pkgs.stdenv.hostPlatform.isDarwin [ pkgs.libiconv ];
            PYO3_PYTHON = "${buildPython}/bin/python";
            # Every cargo invocation honours Cargo.lock as committed (invariant 7).
            cargoExtraArgs = "--locked";
          };
          # The bindings crate's dependencies in the release profile, once. The
          # wheel builds on top of them.
          wheelDeps = craneLib.buildDepsOnly (
            commonArgs
            // {
              pnameSuffix = "-wheel-deps";
              cargoExtraArgs = "--locked --package alliumpy";
            }
          );
          # The wheel, as `just wheel` builds it: maturin, release profile, the
          # workspace Cargo.lock (`locked = true` in the wheel manifest). It links
          # against Nix's libraries and is not a release artefact; the release
          # workflow builds those (decision 0015).
          wheel = craneLib.mkCargoDerivation (
            commonArgs
            // {
              pnameSuffix = "-wheel";
              cargoArtifacts = wheelDeps;
              nativeBuildInputs = [
                buildPython
                pkgs.maturin
              ];
              buildPhaseCargoCommand = ''
                maturin build --release --offline --manifest-path crates/alliumpy/Cargo.toml --out dist
              '';
              doCheck = false;
              doInstallCargoArtifacts = false;
              installPhaseCommand = ''
                mkdir -p "$out"
                cp dist/*.whl "$out"/
              '';
            }
          );

          # The build-shaped gates as sandboxed checks, beside `just check` and
          # never instead of it. They use the recipes' lint tables, features and
          # lockfile. The four cargo checks share one dependency build in the dev
          # profile the recipes use; the wheel smoke uses the wheel, built over
          # its own release-profile dependencies; the Nix-files check builds no
          # crate. The fuzz crate is outside the workspace and outside
          # these checks; `just clippy` and `just fuzz-build` cover it.
          # Every tracked Nix file, as `just nix-check` sees them.
          nixFiles = lib.fileset.toSource {
            root = ./.;
            fileset = lib.fileset.fileFilter (file: file.hasExt "nix") ./.;
          };
          checkArgs = commonArgs // {
            CARGO_PROFILE = "dev";
            cargoExtraArgs = "--locked --workspace --all-features";
          };
          checkDeps = craneLib.buildDepsOnly (checkArgs // { pnameSuffix = "-check-deps"; });
          checks = {
            build = craneLib.cargoBuild (checkArgs // { cargoArtifacts = checkDeps; });
            # `just clippy`'s workspace line.
            clippy = craneLib.cargoClippy (
              checkArgs
              // {
                cargoArtifacts = checkDeps;
                cargoClippyExtraArgs = "--all-targets -- -D warnings";
              }
            );
            # `just test`: nextest over the core, then its doctests. The bindings
            # crate's tests are Python's (decision 0005).
            tests = craneLib.cargoNextest (
              checkArgs
              // {
                cargoArtifacts = checkDeps;
                cargoExtraArgs = "--locked --all-features";
                cargoNextestExtraArgs = "--workspace --exclude alliumpy";
                INSTA_UPDATE = "no";
              }
            );
            doctests = craneLib.cargoDocTest (
              checkArgs
              // {
                cargoArtifacts = checkDeps;
                cargoExtraArgs = "--locked --workspace --exclude alliumpy --all-features";
              }
            );
            # wheel-smoke over the Nix-built wheel, offline: a fresh environment,
            # the wheel alone, the smoke script, the console script.
            wheel-smoke =
              pkgs.runCommand "alliumpy-wheel-smoke"
                {
                  nativeBuildInputs = [ buildPython ];
                  PIP_NO_CACHE_DIR = "1";
                }
                ''
                  python -m venv "$TMPDIR/venv"
                  "$TMPDIR/venv/bin/python" -m pip install --quiet --no-index --no-deps ${wheel}/*.whl
                  "$TMPDIR/venv/bin/python" -I ${./tests/fixtures/smoke}/smoke.py
                  "$TMPDIR/venv/bin/allium" --version
                  "$TMPDIR/venv/bin/allium" check ${./tests/fixtures/smoke}/ok.allium
                  touch "$out"
                '';
            # `just nix-check` over the tracked Nix files.
            nix-format =
              pkgs.runCommand "alliumpy-nix-format"
                {
                  nativeBuildInputs = [
                    pkgs.nixfmt
                    pkgs.statix
                    pkgs.deadnix
                  ];
                }
                ''
                  cd ${nixFiles}
                  files=$(find . -name '*.nix' | sort)
                  [ -n "$files" ] || { echo 'nix-format: no Nix file' >&2; exit 1; }
                  nixfmt --check $files
                  for f in $files; do statix check "$f"; done
                  deadnix --fail $files
                  touch "$out"
                '';
          };
        in
        {
          inherit checks;
          packages = {
            inherit wheel parityReference;
            default = wheel;
          };

          # mkShell, not mkShellNoCC: cargo links through the C compiler, and
          # libfuzzer-sys's build script compiles C++ whenever the fuzz crate builds.
          devShell = pkgs.mkShell {
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
            ++ lib.optionals pkgs.stdenv.hostPlatform.isDarwin [ pkgs.libiconv ];

            # The interpreter pyo3 builds against and the virtual environments
            # are made on; the Justfile reads it rather than search PATH, and
            # refuses to load without it, as the first hook refuses a commit, so
            # it also marks being inside this shell.
            ALLIUMPY_PYTHON = "${python}/bin/python";
            # The metrics gate refuses a rustqual of any other version.
            ALLIUMPY_RUSTQUAL_VERSION = rustqual.version;
            ALLIUMPY_PARITY_REFERENCE = "${parityReference}/bin/allium";
          };
        };
      # One nixpkgs evaluation per system, shared by every output below.
      perSystem = forEachSystem (pkgs: (build pkgs) // { formatter = pkgs.nixfmt-tree; });
      project = f: nixpkgs.lib.mapAttrs (_: f) perSystem;
    in
    {
      formatter = project (s: s.formatter);

      packages = project (s: s.packages);

      checks = project (s: s.checks);

      devShells = project (s: {
        default = s.devShell;
      });
    };
}
