//! Upstream's `allium` command, vendored from `juxt/allium-tools` at v3.6.1.
//!
//! `cli/main.rs`, `cli/test_plan.rs` and `cli/domain_model.rs` are upstream's
//! `crates/allium/src/` files with a provenance header and a block of file-level
//! `#![expect]` attributes. `domain_model.rs` is otherwise unchanged;
//! `test_plan.rs`'s tests read upstream's `v3-lifecycle.allium` from the parity
//! corpus (`tests/fixtures/parity/`) instead of upstream's workspace path; and
//! `main.rs` differs only in these ways:
//!
//! - `mod domain_model; mod test_plan;` became `use super::{domain_model, test_plan};`.
//! - `fn main() -> ExitCode` became `main(args, stdout, stderr) -> i32`, and every
//!   function that prints takes the two handles; `ExitCode::SUCCESS` and
//!   `ExitCode::from(n)` became `0` and `n`.
//! - `print!`, `println!` and `eprintln!` became the macros below, which write to
//!   the handles and panic on a failed write, as upstream's do.
//! - `--version` prints [`crate::ALLIUM_VERSION_STRING`] instead of building the
//!   string from `CARGO_PKG_VERSION`.

use std::ffi::OsString;
use std::io::Write;
use std::panic::{self, AssertUnwindSafe};

/// Upstream's `print!`, on a handle: a failed write panics, as upstream's does.
macro_rules! print_to {
    ($w:expr, $($arg:tt)*) => {
        if let Err(error) = write!($w, $($arg)*) {
            panic!("failed printing to stdout: {error}")
        }
    };
}

/// Upstream's `println!`, on a handle: a failed write panics, as upstream's does.
macro_rules! println_to {
    ($w:expr, $($arg:tt)*) => {
        if let Err(error) = writeln!($w, $($arg)*) {
            panic!("failed printing to stdout: {error}")
        }
    };
}

/// Upstream's `eprintln!`, on a handle: a failed write panics, as upstream's does.
macro_rules! eprintln_to {
    ($w:expr, $($arg:tt)*) => {
        if let Err(error) = writeln!($w, $($arg)*) {
            panic!("failed printing to stderr: {error}")
        }
    };
}

// Upstream's formatting is kept, so that a re-vendor is a plain copy.
#[rustfmt::skip]
mod domain_model;
#[rustfmt::skip]
mod main;
#[rustfmt::skip]
mod test_plan;

/// The exit status of a Rust program whose `main` panicked, as upstream's does on a
/// failed write to a closed pipe.
const PANIC_EXIT_STATUS: i32 = 101;

/// Run upstream's `allium` command on `args` (without the program name), writing
/// to `stdout` and `stderr`, and return its exit status.
///
/// A panic in upstream's code, a failed write included, returns 101 as upstream's
/// binary exits, after the panic hook has reported it.
///
/// ```
/// let mut out = Vec::new();
/// let mut err = Vec::new();
/// let status = alliumpy_core::cli::run(&["--version".into()], &mut out, &mut err);
/// assert_eq!((status, out), (0, format!("{}\n", alliumpy_core::ALLIUM_VERSION_STRING).into_bytes()));
/// ```
pub fn run(args: &[String], stdout: &mut dyn Write, stderr: &mut dyn Write) -> i32 {
    panic::catch_unwind(AssertUnwindSafe(|| main::main(args, stdout, stderr)))
        .unwrap_or(PANIC_EXIT_STATUS)
}

/// [`run`] on arguments as the operating system passed them.
///
/// Upstream reads its arguments with `std::env::args`, which panics on one that is
/// not UTF-8; this writes that panic's message and returns 101, as upstream's binary
/// exits.
///
/// ```
/// let mut out = Vec::new();
/// let status = alliumpy_core::cli::run_os(vec!["-V".into()], &mut out, &mut Vec::new());
/// assert_eq!(status, 0);
/// ```
#[expect(
    clippy::unnecessary_debug_formatting,
    reason = "upstream's panic message prints the argument with Debug"
)]
pub fn run_os(args: Vec<OsString>, stdout: &mut dyn Write, stderr: &mut dyn Write) -> i32 {
    match args
        .into_iter()
        .map(OsString::into_string)
        .collect::<Result<Vec<_>, _>>()
    {
        Ok(args) => run(&args, stdout, stderr),
        Err(arg) => {
            // The message is upstream's panic's; a failure to write it changes nothing.
            let _ = writeln!(
                stderr,
                "called `Result::unwrap()` on an `Err` value: {arg:?}"
            );
            PANIC_EXIT_STATUS
        }
    }
}

#[cfg(test)]
mod tests {
    use std::io::{self, Write};

    // Expected statuses are the reference `allium-cli` 3.6.1's, observed on the
    // parity corpus (`tests/fixtures/parity/`, upstream's files unedited).
    const CORPUS: &str = "../../tests/fixtures/parity";
    const LIFECYCLE: &str =
        "../../tests/fixtures/parity/crates/allium-parser/tests/fixtures/v3-lifecycle.allium";
    const EDGE_CASES: &str = "../../tests/fixtures/parity/crates/allium-parser/tests/fixtures/comprehensive-edge-cases.allium";

    fn run(args: &[&str]) -> (i32, String, String) {
        let args: Vec<String> = args.iter().map(|&arg| arg.to_owned()).collect();
        let (mut out, mut err) = (Vec::new(), Vec::new());
        let status = super::run(&args, &mut out, &mut err);
        (
            status,
            String::from_utf8(out).unwrap(),
            String::from_utf8(err).unwrap(),
        )
    }

    #[test]
    fn version_prints_the_copied_literal_and_exits_0() {
        for flag in ["-V", "--version"] {
            let expected = format!("{}\n", crate::ALLIUM_VERSION_STRING);
            assert_eq!(run(&[flag]), (0, expected, String::new()));
        }
    }

    #[test]
    fn no_arguments_exit_2_with_usage_on_stderr() {
        let expected = "allium: missing command\nRun `allium --help` for usage.\n";
        assert_eq!(run(&[]), (2, String::new(), expected.to_owned()));
    }

    #[test]
    fn unknown_commands_exit_2_with_nothing_on_stdout() {
        for args in [&["frobnicate"][..], &["help", "frobnicate"]] {
            let (status, out, err) = run(args);
            assert_eq!((status, out.as_str()), (2, ""));
            assert!(err.starts_with("allium: unknown command `frobnicate`\n"));
        }
    }

    #[test]
    fn help_forms_print_help_on_stdout_and_exit_0() {
        for args in [&["help"][..], &["-h"], &["--help"]] {
            let (status, out, _) = run(args);
            assert_eq!(status, 0);
            assert!(out.starts_with("allium - validate, parse and analyse"));
        }
        for command in ["check", "analyse", "parse", "plan", "model"] {
            for args in [
                &["help", command][..],
                &[command, "--help"],
                &[command, "-h"],
            ] {
                let (status, out, _) = run(args);
                assert_eq!(status, 0);
                assert!(out.starts_with(&format!("allium {command} - ")));
            }
        }
    }

    /// The number of `.allium` files under the corpus, walked with an explicit stack.
    fn corpus_files() -> usize {
        let mut pending = vec![std::path::PathBuf::from(CORPUS)];
        let mut count = 0;
        while let Some(dir) = pending.pop() {
            let paths = std::fs::read_dir(dir)
                .unwrap()
                .map(|entry| entry.unwrap().path());
            let (dirs, files): (Vec<_>, Vec<_>) = paths.partition(|path| path.is_dir());
            count += files
                .iter()
                .filter(|path| path.extension().is_some_and(|ext| ext == "allium"))
                .count();
            pending.extend(dirs);
        }
        count
    }

    #[test]
    fn check_and_analyse_of_the_corpus_report_every_file_and_exit_1() {
        let files = corpus_files();
        assert!(files > 0);
        for command in ["check", "analyse"] {
            let (status, out, _) = run(&[command, CORPUS]);
            assert_eq!(status, 1);
            let reported = out.matches(&format!("\"command\": \"{command}\"")).count();
            assert_eq!(reported, files);
        }
    }

    #[test]
    fn check_exits_1_on_a_file_with_an_error_or_warning() {
        let (status, out, _) = run(&["check", EDGE_CASES]);
        assert_eq!(status, 1);
        assert!(
            out.contains("\"severity\": \"error\"") || out.contains("\"severity\": \"warning\"")
        );
    }

    #[test]
    fn single_file_commands_exit_0_on_a_file_that_parses() {
        for command in ["parse", "plan", "model"] {
            let (status, out, _) = run(&[command, LIFECYCLE]);
            assert_eq!(status, 0);
            assert!(out.contains("\"diagnostics\""));
        }
    }

    #[test]
    fn missing_inputs_exit_2_and_unreadable_files_exit_1() {
        for command in ["parse", "plan", "model"] {
            assert_eq!(run(&[command]).0, 2);
            assert_eq!(run(&[command, LIFECYCLE, LIFECYCLE]).0, 2);
            assert_eq!(run(&[command, "does-not-exist.allium"]).0, 1);
        }
        assert_eq!(
            run(&["check"]),
            (2, String::new(), "No .allium files found.\n".to_owned())
        );
        assert_eq!(run(&["check", "does-not-exist.allium"]).0, 1);
    }

    struct ClosedPipe;

    impl Write for ClosedPipe {
        fn write(&mut self, _: &[u8]) -> io::Result<usize> {
            Err(io::ErrorKind::BrokenPipe.into())
        }

        fn flush(&mut self) -> io::Result<()> {
            Ok(())
        }
    }

    #[cfg(unix)]
    #[test]
    fn an_argument_that_is_not_utf8_exits_101_as_upstreams_panic_does() {
        use std::os::unix::ffi::OsStringExt;
        let args = vec![
            "check".into(),
            std::ffi::OsString::from_vec(b"\xff.allium".to_vec()),
        ];
        let (mut out, mut err) = (Vec::new(), Vec::new());
        assert_eq!(super::run_os(args, &mut out, &mut err), 101);
        assert_eq!(
            (out, String::from_utf8(err).unwrap()),
            (
                Vec::new(),
                "called `Result::unwrap()` on an `Err` value: \"\\xFF.allium\"\n".to_owned()
            )
        );
    }

    #[test]
    fn utf8_arguments_run_the_command() {
        let (mut out, mut err) = (Vec::new(), Vec::new());
        assert_eq!(super::run_os(vec!["-V".into()], &mut out, &mut err), 0);
        assert_eq!(
            out,
            format!("{}\n", crate::ALLIUM_VERSION_STRING).into_bytes()
        );
    }

    #[test]
    fn a_failed_write_exits_101_as_upstreams_panic_does() {
        assert_eq!(
            super::run(&["--version".to_owned()], &mut ClosedPipe, &mut Vec::new()),
            101
        );
    }
}
