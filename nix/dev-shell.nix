# The development shell: the only environment a recipe runs in (decision 0018). The
# Justfile refuses to run outside it, and `just check-toolchain` proves it is this one.
{ pkgs, inputs }:
let
  inherit (pkgs) lib;

  # rust-toolchain.toml stays the single owner of the channel, profile and components.
  rustToolchain = pkgs.rust-bin.fromRustupToolchainFile ../rust-toolchain.toml;

  # Python 3.14 for the gate's tools; the wheel itself targets abi3-py311. pytest, mypy
  # and the checkers live in this interpreter's environment, and py-develop's venv sees
  # them through --system-site-packages.
  python = pkgs.python314;
  tooling = python.pkgs.callPackage ./biscuit-games-tooling.nix {
    src = inputs.biscuit-games-tooling;
  };
  pythonEnv = python.withPackages (ps: [
    ps.pytest
    ps.mypy
    tooling
  ]);

  rustqual = pkgs.callPackage ./rustqual.nix { };

  # What the shell is built from. check-toolchain hashes the same files in the worktree
  # and refuses a shell entered before one of them changed (a pull, a lock, an edit).
  nixFiles = lib.sort lib.lessThan (
    map (name: "./nix/${name}") (
      lib.attrNames (lib.filterAttrs (name: _: lib.hasSuffix ".nix" name) (builtins.readDir ../nix))
    )
  );
  envFiles = [
    "./flake.nix"
    "./flake.lock"
    "./rust-toolchain.toml"
  ]
  ++ nixFiles;
  fingerprint = builtins.hashString "sha256" (
    lib.concatMapStrings (file: builtins.hashFile "sha256" (../. + lib.removePrefix "." file)) envFiles
  );

  packages = [
    rustToolchain
    pythonEnv
    rustqual

    # The runner, the hook runner and git.
    pkgs.just
    pkgs.prek
    pkgs.git

    # Cargo subcommands and the TOML formatter the Rust gates call.
    pkgs.cargo-nextest
    pkgs.cargo-llvm-cov
    pkgs.cargo-deny
    pkgs.cargo-insta
    pkgs.cargo-shear
    pkgs.cargo-hack
    pkgs.cargo-fuzz
    pkgs.cargo-mutants
    pkgs.taplo

    # The Python side: maturin builds the extension, uv makes the venvs, ruff lints.
    pkgs.maturin
    pkgs.uv
    pkgs.ruff

    # The checkers the hooks call (.pre-commit-config.yaml).
    pkgs.typos
    pkgs.lychee
    pkgs.shellcheck
    pkgs.actionlint
    pkgs.markdownlint-cli2
    pkgs.editorconfig-checker
    pkgs.ripsecrets
    pkgs.nixfmt
  ]
  ++ lib.optionals pkgs.stdenv.hostPlatform.isDarwin [ pkgs.libiconv ];
in
pkgs.mkShell {
  name = "alliumpy-dev";
  inherit packages;

  env = {
    ALLIUMPY_DEV_SHELL = "1";
    ALLIUMPY_RUST_TOOLCHAIN = "${rustToolchain}";
    # The bin directories of exactly the packages above, plus the two the checkers'
    # wrapped scripts put first on PATH for the recipes bg-project-check runs: their own
    # package's and the interpreter's under pythonEnv. check-toolchain refuses a gate
    # tool from anywhere else, another store path included.
    ALLIUMPY_TOOL_PATH = lib.makeBinPath (
      packages
      ++ [
        tooling
        python
      ]
    );
    ALLIUMPY_ENV_FILES = lib.concatStringsSep " " envFiles;
    ALLIUMPY_ENV_FINGERPRINT = fingerprint;
    # Only for the string context: the inputs' source trees join the shell's closure,
    # so the GC root `just sync` records keeps them and re-entering the shell is offline.
    ALLIUMPY_FLAKE_INPUTS = "${inputs.nixpkgs} ${inputs.rust-overlay} ${inputs.biscuit-games-tooling}";
    # Every cargo invocation compiles the bindings against this interpreter.
    PYO3_PYTHON = "${pythonEnv}/bin/python";
    # stdenv would add `-rpath $out/lib` to every link, and in a shell $out is a path
    # under the worktree, which would then be baked into every binary built here.
    NIX_NO_SELF_RPATH = "1";
    # uv uses the shell's interpreter and never downloads one.
    UV_PYTHON_DOWNLOADS = "never";
    UV_PYTHON_PREFERENCE = "only-system";
  };
}
