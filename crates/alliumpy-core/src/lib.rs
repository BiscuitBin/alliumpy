//! Interpreter-independent conversion of upstream Allium parser diagnostics.

/// Parse an Allium source, returning diagnostics in source order.
///
/// ```
/// assert_eq!(alliumpy_core::parse("-- allium: 1\n"), []);
/// ```
#[must_use]
pub fn parse(source: &str) -> Vec<Diagnostic> {
    let source_map = allium_parser::lexer::SourceMap::new(source);
    allium_parser::parse(source)
        .diagnostics
        .iter()
        .map(|diagnostic| {
            let (line, col) = source_map.line_col(diagnostic.span.start);
            Diagnostic {
                line: line + 1,
                col: col + 1,
                severity: convert_severity(diagnostic.severity),
                message: diagnostic.message.clone(),
                code: diagnostic.code.map(str::to_owned),
            }
        })
        .collect()
}

/// The upstream version wrapped by this crate.
pub const ALLIUM_VERSION: &str = "3.6.1";

/// Upstream's CLI version output, from `crates/allium/src/main.rs` at v3.6.1.
pub const ALLIUM_VERSION_STRING: &str = "allium 3.6.1 (language versions: 1, 2, 3)";

/// The importance of an upstream diagnostic.
#[non_exhaustive]
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Severity {
    /// Source contains an error.
    Error,
    /// Source merits a warning.
    Warning,
    /// Informational diagnostic.
    Info,
}

/// An upstream diagnostic with a one-based source location.
#[non_exhaustive]
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct Diagnostic {
    /// One-based line number.
    pub line: u32,
    /// One-based byte column, matching the upstream CLI.
    pub col: u32,
    /// Importance of the diagnostic.
    pub severity: Severity,
    /// Upstream's message, unchanged.
    pub message: String,
    /// Optional upstream diagnostic code.
    pub code: Option<String>,
}

const fn convert_severity(severity: allium_parser::diagnostic::Severity) -> Severity {
    match severity {
        allium_parser::diagnostic::Severity::Error => Severity::Error,
        allium_parser::diagnostic::Severity::Warning => Severity::Warning,
        allium_parser::diagnostic::Severity::Info => Severity::Info,
    }
}

#[cfg(test)]
mod tests {
    #[test]
    fn empty_source_reports_upstreams_missing_version_warning() {
        assert_eq!(
            super::parse(""),
            [super::Diagnostic {
                line: 1,
                col: 1,
                severity: super::Severity::Warning,
                message: "missing version marker; expected '-- allium: 1' as the first line".into(),
                code: None,
            }]
        );
    }

    #[test]
    fn syntax_error_uses_upstream_cli_coordinates() {
        // U v3.6.1 lexer::SourceMap::line_col is zero-based. main.rs
        // diagnostic_to_json adds one to both: '?' at offset 13 is (2, 1).
        let diagnostics = super::parse("-- allium: 1\n?\n");
        assert_eq!((diagnostics[0].line, diagnostics[0].col), (2, 1));
        assert_eq!(diagnostics[0].severity, super::Severity::Error);
    }

    #[test]
    fn version_output_identifies_upstream() {
        assert!(
            super::ALLIUM_VERSION_STRING.starts_with(&format!("allium {} ", super::ALLIUM_VERSION))
        );
    }

    #[test]
    fn error_severity_is_preserved() {
        assert_eq!(
            super::convert_severity(allium_parser::diagnostic::Severity::Error),
            super::Severity::Error
        );
    }

    #[test]
    fn warning_severity_is_preserved() {
        assert_eq!(
            super::convert_severity(allium_parser::diagnostic::Severity::Warning),
            super::Severity::Warning
        );
    }

    #[test]
    fn info_severity_is_preserved() {
        assert_eq!(
            super::convert_severity(allium_parser::diagnostic::Severity::Info),
            super::Severity::Info
        );
    }
}
