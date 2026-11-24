//! Upstream's `check` and `analyse` results, captured from the vendored command.

use std::fmt;

use serde::Deserialize;

use crate::{Diagnostic, Severity};

/// What one run of `allium check` or `allium analyse` reported.
#[non_exhaustive]
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct Report {
    /// The exit status the command returned.
    pub status: i32,
    /// One report per file the command read, in the order it printed them.
    pub files: Vec<FileReport>,
    /// What the command wrote to stderr, such as an unreadable file's error.
    pub stderr: String,
}

/// The command's report on one specification file.
#[non_exhaustive]
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct FileReport {
    /// The path as the command printed it.
    pub spec_file: String,
    /// The file's diagnostics, in the command's order.
    pub diagnostics: Vec<Diagnostic>,
    /// The file's findings, in the command's order; `check` reports none.
    pub findings: Vec<Finding>,
}

/// One `analyse` finding.
#[non_exhaustive]
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct Finding {
    /// The finding's `type`, such as `dead_transition`.
    pub kind: String,
    /// Upstream's one-line summary.
    pub summary: String,
    /// The entities the finding names.
    pub affected_entities: Vec<String>,
    /// The finding's complete JSON object, every key the command printed included.
    pub json: String,
}

/// Why the command's output could not be returned as a [`Report`].
#[non_exhaustive]
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum ReportError {
    /// The command panicked and exited 101.
    Crashed,
    /// The command printed something other than its JSON reports, such as its help.
    Malformed,
}

impl fmt::Display for ReportError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(match self {
            Self::Crashed => "the allium command panicked (exit status 101)",
            Self::Malformed => "the allium command printed output that is not its JSON reports",
        })
    }
}

impl std::error::Error for ReportError {}

/// Run upstream's `allium check` on `paths`, as the command would, capturing its output.
///
/// The status is the command's exit status: 0 when no file has an error or a
/// warning, 1 when one does or a file cannot be read, and 2 when no `.allium` file
/// is found.
///
/// # Errors
///
/// [`ReportError::Crashed`] when the command panics, and [`ReportError::Malformed`]
/// when it prints something other than its reports, as `--help` among the paths does.
///
/// ```
/// let report = alliumpy_core::report::check(&[]).unwrap();
/// assert_eq!((report.status, report.stderr.as_str()), (2, "No .allium files found.\n"));
/// ```
pub fn check(paths: &[String]) -> Result<Report, ReportError> {
    run("check", paths)
}

/// Run upstream's `allium analyse` on `paths`, as the command would, capturing its output.
///
/// The status is the command's exit status: 0 when no file has a finding, 1 when one
/// does or a file cannot be read, and 2 when no `.allium` file is found. An error
/// diagnostic alone leaves it 0.
///
/// # Errors
///
/// As [`check`].
///
/// ```
/// let report = alliumpy_core::report::analyse(&["missing.allium".to_owned()]).unwrap();
/// assert_eq!((report.status, report.files.len()), (1, 0));
/// ```
pub fn analyse(paths: &[String]) -> Result<Report, ReportError> {
    run("analyse", paths)
}

fn run(command: &str, paths: &[String]) -> Result<Report, ReportError> {
    let args: Vec<String> = std::iter::once(command.to_owned())
        .chain(paths.iter().cloned())
        .collect();
    let (mut stdout, mut stderr) = (Vec::new(), Vec::new());
    let status = crate::cli::run(&args, &mut stdout, &mut stderr);
    from_output(status, &stdout, &stderr)
}

/// The command's exit status that means its `main` panicked.
const CRASHED: i32 = 101;

fn from_output(status: i32, stdout: &[u8], stderr: &[u8]) -> Result<Report, ReportError> {
    if status == CRASHED {
        return Err(ReportError::Crashed);
    }
    let files = serde_json::Deserializer::from_slice(stdout)
        .into_iter::<RawFileReport>()
        .map(|raw| raw.map_err(|_| ReportError::Malformed)?.convert())
        .collect::<Result<_, _>>()?;
    Ok(Report {
        status,
        files,
        stderr: String::from_utf8_lossy(stderr).into_owned(),
    })
}

/// One printed object, as upstream's `run_multi_file` writes it.
#[derive(Deserialize)]
struct RawFileReport {
    spec_file: String,
    diagnostics: Vec<RawDiagnostic>,
    findings: Vec<serde_json::Value>,
}

/// One diagnostic, as upstream's `diagnostic_to_json` writes it.
#[derive(Deserialize)]
struct RawDiagnostic {
    code: Option<String>,
    severity: RawSeverity,
    message: String,
    location: RawLocation,
}

#[derive(Deserialize)]
#[serde(rename_all = "lowercase")]
enum RawSeverity {
    Error,
    Warning,
    Info,
}

#[derive(Deserialize)]
struct RawLocation {
    line: u32,
    col: u32,
}

/// The keys every upstream finding carries (`allium_parser::analysis`).
#[derive(Deserialize)]
struct RawFinding {
    #[serde(rename = "type")]
    kind: String,
    summary: String,
    affected_entities: Vec<String>,
}

impl RawFileReport {
    fn convert(self) -> Result<FileReport, ReportError> {
        let findings = self
            .findings
            .into_iter()
            .map(convert_finding)
            .collect::<Result<_, _>>()?;
        Ok(FileReport {
            spec_file: self.spec_file,
            diagnostics: self
                .diagnostics
                .into_iter()
                .map(RawDiagnostic::convert)
                .collect(),
            findings,
        })
    }
}

impl RawDiagnostic {
    fn convert(self) -> Diagnostic {
        Diagnostic {
            line: self.location.line,
            col: self.location.col,
            severity: match self.severity {
                RawSeverity::Error => Severity::Error,
                RawSeverity::Warning => Severity::Warning,
                RawSeverity::Info => Severity::Info,
            },
            message: self.message,
            code: self.code,
        }
    }
}

fn convert_finding(json: serde_json::Value) -> Result<Finding, ReportError> {
    let text = json.to_string();
    let raw = RawFinding::deserialize(json).map_err(|_| ReportError::Malformed)?;
    Ok(Finding {
        kind: raw.kind,
        summary: raw.summary,
        affected_entities: raw.affected_entities,
        json: text,
    })
}

#[cfg(test)]
mod tests {
    use super::{Report, ReportError, analyse, check, from_output};
    use crate::{Diagnostic, Severity};

    // Expected values are the reference `allium-cli` 3.6.1's JSON for the same paths.
    const OK: &str = "../../tests/fixtures/smoke/ok.allium";
    const BROKEN: &str = "../../tests/fixtures/smoke/broken.allium";
    const CORPUS: &str = "../../tests/fixtures/parity";
    const BROKEN_MESSAGE: &str = "expected declaration (entity, rule, enum, value, config, surface, actor, given, default, variant, deferred, use, open question, contract, invariant), found '?'";

    fn paths(paths: &[&str]) -> Vec<String> {
        paths.iter().map(|&path| path.to_owned()).collect()
    }

    #[test]
    fn a_clean_file_reports_no_diagnostics_and_status_0() {
        for run in [check, analyse] {
            let report = run(&paths(&[OK])).unwrap();
            assert_eq!((report.status, report.stderr.as_str()), (0, ""));
            assert_eq!(report.files.len(), 1);
            assert_eq!(report.files[0].spec_file, OK);
            assert_eq!(report.files[0].diagnostics, []);
            assert_eq!(report.files[0].findings, []);
        }
    }

    #[test]
    fn an_error_fails_check_but_not_analyse() {
        let expected = vec![Diagnostic {
            line: 5,
            col: 9,
            severity: Severity::Error,
            message: BROKEN_MESSAGE.to_owned(),
            code: None,
        }];
        let checked = check(&paths(&[BROKEN])).unwrap();
        assert_eq!(
            (checked.status, &checked.files[0].diagnostics),
            (1, &expected)
        );
        let analysed = analyse(&paths(&[BROKEN])).unwrap();
        assert_eq!(
            (analysed.status, &analysed.files[0].diagnostics),
            (0, &expected)
        );
    }

    #[test]
    fn analyse_of_the_corpus_reports_typed_findings() {
        let report = analyse(&paths(&[CORPUS])).unwrap();
        assert_eq!(report.status, 1);
        let findings: Vec<_> = report
            .files
            .iter()
            .flat_map(|file| &file.findings)
            .collect();
        assert_ne!(findings.len(), 0);
        for finding in findings {
            let json: serde_json::Value = serde_json::from_str(&finding.json).unwrap();
            assert_eq!(json["type"], finding.kind.as_str());
            assert_eq!(json["summary"], finding.summary.as_str());
            assert_eq!(
                json["affected_entities"],
                serde_json::json!(finding.affected_entities)
            );
        }
    }

    #[test]
    fn check_reports_codes_and_every_severity() {
        let report = check(&paths(&[CORPUS])).unwrap();
        let diagnostics: Vec<_> = report
            .files
            .iter()
            .flat_map(|file| &file.diagnostics)
            .collect();
        assert!(diagnostics.iter().any(|d| d.code.is_some()));
        for severity in [Severity::Error, Severity::Warning, Severity::Info] {
            assert!(diagnostics.iter().any(|d| d.severity == severity));
        }
    }

    #[test]
    fn an_unreadable_file_exits_1_with_no_report_for_it() {
        let report = check(&paths(&["does-not-exist.allium", OK])).unwrap();
        assert_eq!(report.status, 1);
        assert_eq!(report.files.len(), 1);
        assert_eq!(report.files[0].spec_file, OK);
        assert!(report.stderr.starts_with("does-not-exist.allium: "));
    }

    #[test]
    fn no_specification_found_exits_2() {
        let expected = Report {
            status: 2,
            files: Vec::new(),
            stderr: "No .allium files found.\n".to_owned(),
        };
        assert_eq!(check(&[]).unwrap(), expected);
        assert_eq!(analyse(&[]).unwrap(), expected);
    }

    #[cfg(unix)]
    #[test]
    fn an_unreadable_directory_is_skipped() {
        use std::os::unix::fs::PermissionsExt;
        // A specification inside, so the status shows the directory was not listed.
        let dir = std::env::temp_dir().join(format!("alliumpy-report-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        std::fs::copy(OK, dir.join("ok.allium")).unwrap();
        std::fs::set_permissions(&dir, std::fs::Permissions::from_mode(0o000)).unwrap();
        // Root lists the directory regardless, so the test has nothing to prove there.
        let enforced = std::fs::read_dir(&dir).is_err();
        let report = check(&[dir.display().to_string()]);
        std::fs::set_permissions(&dir, std::fs::Permissions::from_mode(0o700)).unwrap();
        std::fs::remove_dir_all(&dir).unwrap();
        if !enforced {
            return;
        }
        let report = report.unwrap();
        assert_eq!(
            (report.status, report.files, report.stderr.as_str()),
            (2, Vec::new(), "No .allium files found.\n")
        );
    }

    #[test]
    fn help_is_not_a_report() {
        assert_eq!(check(&paths(&["--help"])), Err(ReportError::Malformed));
    }

    #[test]
    fn a_panic_is_an_error_whatever_was_printed() {
        assert_eq!(from_output(101, b"", b""), Err(ReportError::Crashed));
    }

    #[test]
    fn a_finding_without_upstreams_keys_is_malformed() {
        let stdout =
            br#"{"spec_file": "a.allium", "diagnostics": [], "findings": [{"type": "x"}]}"#;
        assert_eq!(from_output(1, stdout, b""), Err(ReportError::Malformed));
    }

    #[test]
    fn errors_have_stable_messages() {
        assert_eq!(
            ReportError::Crashed.to_string(),
            "the allium command panicked (exit status 101)"
        );
        assert_eq!(
            ReportError::Malformed.to_string(),
            "the allium command printed output that is not its JSON reports"
        );
    }
}
