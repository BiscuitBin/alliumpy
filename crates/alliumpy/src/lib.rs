//! Thin Python wrappers over the interpreter-independent Allium core.

use pyo3::prelude::*;
use pyo3::types::PyString;
use std::ffi::OsString;
use std::io::Write;

pyo3::create_exception!(
    alliumpy,
    AlliumError,
    pyo3::exceptions::PyValueError,
    "An Allium operation failed."
);

/// An immutable diagnostic returned by the upstream parser.
#[pyclass(frozen, eq, hash, module = "alliumpy._alliumpy")]
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
struct Diagnostic {
    inner: alliumpy_core::Diagnostic,
}

#[pymethods]
impl Diagnostic {
    /// One-based source line.
    #[getter]
    const fn line(&self) -> u32 {
        self.inner.line
    }

    /// One-based source byte column.
    #[getter]
    const fn col(&self) -> u32 {
        self.inner.col
    }

    /// Importance as error, warning or info.
    #[getter]
    const fn severity(&self) -> &'static str {
        match self.inner.severity {
            alliumpy_core::Severity::Error => "error",
            alliumpy_core::Severity::Warning => "warning",
            // The core enum is non-exhaustive across the crate boundary.
            _ => "info",
        }
    }

    /// Upstream's diagnostic message.
    #[getter]
    fn message(&self) -> &str {
        &self.inner.message
    }

    /// Optional upstream diagnostic code.
    #[getter]
    fn code(&self) -> Option<&str> {
        self.inner.code.as_deref()
    }

    fn __repr__(&self, py: Python<'_>) -> PyResult<String> {
        let code = match self.code() {
            Some(code) => quote(py, code)?,
            None => "None".to_owned(),
        };
        Ok(format!(
            "Diagnostic(line={}, col={}, severity={}, message={}, code={})",
            self.line(),
            self.col(),
            quote(py, self.severity())?,
            quote(py, self.message())?,
            code
        ))
    }
}

/// Python's `repr` of a string.
fn quote(py: Python<'_>, value: &str) -> PyResult<String> {
    Ok(PyString::new(py, value).repr()?.to_str()?.to_owned())
}

/// Python's `repr` of a list, given each item's.
fn list_repr(items: impl IntoIterator<Item = PyResult<String>>) -> PyResult<String> {
    let items: Vec<String> = items.into_iter().collect::<PyResult<_>>()?;
    Ok(format!("[{}]", items.join(", ")))
}

/// One `analyse` finding as upstream's command printed it.
#[pyclass(frozen, eq, hash, module = "alliumpy._alliumpy")]
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
struct Finding {
    inner: alliumpy_core::report::Finding,
}

#[pymethods]
impl Finding {
    /// The finding's type.
    #[getter]
    #[pyo3(name = "type")]
    fn kind(&self) -> &str {
        &self.inner.kind
    }

    /// Upstream's one-line summary.
    #[getter]
    fn summary(&self) -> &str {
        &self.inner.summary
    }

    /// The entities the finding names.
    #[getter]
    fn affected_entities(&self) -> Vec<String> {
        self.inner.affected_entities.clone()
    }

    /// The finding's complete JSON object.
    #[getter]
    fn json(&self) -> &str {
        &self.inner.json
    }

    fn __repr__(&self, py: Python<'_>) -> PyResult<String> {
        let entities = list_repr(self.inner.affected_entities.iter().map(|e| quote(py, e)))?;
        Ok(format!(
            "Finding(type={}, summary={}, affected_entities={}, json={})",
            quote(py, self.kind())?,
            quote(py, self.summary())?,
            entities,
            quote(py, self.json())?
        ))
    }
}

/// The command's report on one specification file.
#[pyclass(frozen, eq, hash, module = "alliumpy._alliumpy")]
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
struct FileReport {
    inner: alliumpy_core::report::FileReport,
}

#[pymethods]
impl FileReport {
    /// The path as the command printed it.
    #[getter]
    fn spec_file(&self) -> &str {
        &self.inner.spec_file
    }

    /// The file's diagnostics in the command's order.
    #[getter]
    fn diagnostics(&self) -> Vec<Diagnostic> {
        self.inner
            .diagnostics
            .iter()
            .map(|inner| Diagnostic {
                inner: inner.clone(),
            })
            .collect()
    }

    /// The file's findings in the command's order.
    #[getter]
    fn findings(&self) -> Vec<Finding> {
        self.inner
            .findings
            .iter()
            .map(|inner| Finding {
                inner: inner.clone(),
            })
            .collect()
    }

    fn __repr__(&self, py: Python<'_>) -> PyResult<String> {
        Ok(format!(
            "FileReport(spec_file={}, diagnostics={}, findings={})",
            quote(py, self.spec_file())?,
            list_repr(self.diagnostics().iter().map(|d| d.__repr__(py)))?,
            list_repr(self.findings().iter().map(|f| f.__repr__(py)))?
        ))
    }
}

/// What one run of `allium check` or `allium analyse` reported.
#[pyclass(frozen, eq, hash, module = "alliumpy._alliumpy")]
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
struct Report {
    inner: alliumpy_core::report::Report,
}

#[pymethods]
impl Report {
    /// The command's exit status.
    #[getter]
    const fn status(&self) -> i32 {
        self.inner.status
    }

    /// One report per file the command read.
    #[getter]
    fn files(&self) -> Vec<FileReport> {
        self.inner
            .files
            .iter()
            .map(|inner| FileReport {
                inner: inner.clone(),
            })
            .collect()
    }

    /// What the command wrote to stderr.
    #[getter]
    fn stderr(&self) -> &str {
        &self.inner.stderr
    }

    fn __repr__(&self, py: Python<'_>) -> PyResult<String> {
        Ok(format!(
            "Report(status={}, files={}, stderr={})",
            self.status(),
            list_repr(self.files().iter().map(|f| f.__repr__(py)))?,
            quote(py, self.stderr())?
        ))
    }
}

/// Run a report command with the interpreter released, as the command would run.
fn report(
    py: Python<'_>,
    run: fn(&[String]) -> Result<alliumpy_core::report::Report, alliumpy_core::report::ReportError>,
    paths: Vec<String>,
) -> PyResult<Report> {
    py.detach(move || run(&paths))
        .map(|inner| Report { inner })
        .map_err(|error| AlliumError::new_err(error.to_string()))
}

/// Run upstream's `allium check` on `paths`, capturing its reports and status.
#[pyfunction]
fn check(py: Python<'_>, paths: Vec<String>) -> PyResult<Report> {
    report(py, alliumpy_core::report::check, paths)
}

/// Run upstream's `allium analyse` on `paths`, capturing its reports and status.
#[pyfunction]
fn analyse(py: Python<'_>, paths: Vec<String>) -> PyResult<Report> {
    report(py, alliumpy_core::report::analyse, paths)
}

/// Parse source with upstream Allium, preserving diagnostic order.
#[pyfunction]
fn parse(source: &str) -> Vec<Diagnostic> {
    alliumpy_core::parse(source)
        .into_iter()
        .map(|inner| Diagnostic { inner })
        .collect()
}

/// Run upstream's `allium` command on the process's own stdout and stderr.
#[pyfunction(name = "_run_cli")]
fn run_cli(args: Vec<OsString>) -> i32 {
    let mut stdout = std::io::stdout();
    let status = alliumpy_core::cli::run_os(args, &mut stdout, &mut std::io::stderr());
    // Upstream's binary flushes stdout as it exits and ignores a failure there.
    let _ = stdout.flush();
    status
}

/// The native module used by the Python package.
#[pymodule]
fn _alliumpy(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<Diagnostic>()?;
    module.add_class::<FileReport>()?;
    module.add_class::<Finding>()?;
    module.add_class::<Report>()?;
    module.add_function(wrap_pyfunction!(parse, module)?)?;
    module.add_function(wrap_pyfunction!(check, module)?)?;
    module.add_function(wrap_pyfunction!(analyse, module)?)?;
    module.add_function(wrap_pyfunction!(run_cli, module)?)?;
    module.add("AlliumError", module.py().get_type::<AlliumError>())?;
    module.add("ALLIUM_VERSION", alliumpy_core::ALLIUM_VERSION)?;
    module.add(
        "ALLIUM_VERSION_STRING",
        alliumpy_core::ALLIUM_VERSION_STRING,
    )?;
    Ok(())
}
