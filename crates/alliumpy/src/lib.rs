//! Thin Python wrappers over the interpreter-independent Allium core.

use pyo3::prelude::*;
use pyo3::types::PyString;

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
        let severity = PyString::new(py, self.severity()).repr()?;
        let message = PyString::new(py, self.message()).repr()?;
        let code = self
            .code()
            .map(|s| PyString::new(py, s).repr())
            .transpose()?;
        let code = match code.as_ref() {
            Some(value) => value.to_str()?,
            None => "None",
        };
        Ok(format!(
            "Diagnostic(line={}, col={}, severity={}, message={}, code={})",
            self.line(),
            self.col(),
            severity,
            message,
            code
        ))
    }
}

/// Parse source with upstream Allium, preserving diagnostic order.
#[pyfunction]
fn parse(source: &str) -> Vec<Diagnostic> {
    alliumpy_core::parse(source)
        .into_iter()
        .map(|inner| Diagnostic { inner })
        .collect()
}

/// The native module used by the Python package.
#[pymodule]
fn _alliumpy(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<Diagnostic>()?;
    module.add_function(wrap_pyfunction!(parse, module)?)?;
    module.add("AlliumError", module.py().get_type::<AlliumError>())?;
    module.add("ALLIUM_VERSION", alliumpy_core::ALLIUM_VERSION)?;
    module.add(
        "ALLIUM_VERSION_STRING",
        alliumpy_core::ALLIUM_VERSION_STRING,
    )?;
    Ok(())
}
