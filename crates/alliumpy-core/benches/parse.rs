//! Benchmarks for the conversion layer, run by `just bench`.

fn main() {
    divan::main();
}

/// Parsing the smoke fixture that upstream accepts, the source passed through
/// `divan::black_box` so that the work cannot be hoisted.
#[divan::bench]
fn ok() -> Vec<alliumpy_core::Diagnostic> {
    alliumpy_core::parse(divan::black_box(include_str!(
        "../../../tests/fixtures/smoke/ok.allium"
    )))
}

/// Parsing the smoke fixture that upstream rejects, so the diagnostics'
/// conversion is part of the measurement.
#[divan::bench]
fn broken() -> Vec<alliumpy_core::Diagnostic> {
    alliumpy_core::parse(divan::black_box(include_str!(
        "../../../tests/fixtures/smoke/broken.allium"
    )))
}
