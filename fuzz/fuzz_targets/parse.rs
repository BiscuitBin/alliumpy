//! Arbitrary bytes through `alliumpy_core::parse`.
#![no_main]

use libfuzzer_sys::fuzz_target;

// Invalid UTF-8 is ordinary input that `parse`, which takes `&str`, never sees.
// Valid text goes through the parser and the conversion layer; a panic in either,
// such as a span outside the source, is the crash libFuzzer records. Every
// location is one-based (CONVENTIONS.md §9), so a zero is a conversion defect.
fn parse(data: &[u8]) {
    if let Ok(source) = std::str::from_utf8(data) {
        for diagnostic in alliumpy_core::parse(source) {
            assert!(
                diagnostic.line >= 1 && diagnostic.col >= 1,
                "not one-based: {diagnostic:?}"
            );
        }
    }
}

fuzz_target!(|data: &[u8]| parse(data));
