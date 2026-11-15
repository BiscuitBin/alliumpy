# The shared checkers every Biscuit Games repository runs (decision 0002): bg-project-check,
# bg-validate-docs, bg-validate-agents and bg-ripsecrets. The source is the flake input
# pinned in flake.lock; the version is read from it, so the tag in flake.nix is the only
# copy.
{
  lib,
  buildPythonPackage,
  uv-build,
  src,
}:
let
  manifest = lib.importTOML "${src}/pyproject.toml";
in
buildPythonPackage {
  pname = manifest.project.name;
  inherit (manifest.project) version;
  inherit src;
  pyproject = true;
  # The package pins uv_build>=0.11,<0.12 for its own uv-run builds; nixpkgs carries a
  # later uv-build, and the backend's output for a pure-Python package is the same.
  postPatch = ''
    substituteInPlace pyproject.toml --replace-fail '"uv_build>=0.11,<0.12"' '"uv_build"'
  '';
  build-system = [ uv-build ];
  pythonImportsCheck = [ "biscuit_games_tooling" ];
  meta.mainProgram = "bg-project-check";
}
