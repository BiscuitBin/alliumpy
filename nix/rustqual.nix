# The metrics gate's analyser (decision 0007), which nixpkgs does not carry. Built in the
# sandbox from the crates.io source at the version below, with the crate's own Cargo.lock,
# against hashes this file pins. A bump changes the version and both hashes: set each
# hash to "" and the failing build prints the right one.
{
  lib,
  rustPlatform,
  fetchCrate,
}:
rustPlatform.buildRustPackage rec {
  pname = "rustqual";
  # renovate: datasource=crate depName=rustqual
  version = "1.8.3";
  src = fetchCrate {
    inherit pname version;
    hash = "sha256-xplBYaftBxCRwNZwyoHU68vPi1ooQ2krckwi0RoJ0pM=";
  };
  cargoHash = "sha256-oz6R8k7NoE2Gf51N7ZCFaPU+ij/AL315qFzdMz6hCh4=";
  # The crate's tests read fixtures the published crate does not ship.
  doCheck = false;
  meta = {
    description = "Code quality metrics for Rust";
    license = lib.licenses.mit;
    mainProgram = "rustqual";
  };
}
