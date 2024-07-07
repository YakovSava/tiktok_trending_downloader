use std::fs;
use pyo3::prelude::*;

#[pyfunction]
fn reader(filename:String) -> String {
	let content = fs::read_to_string(filename).unwrap();
	return content;
}

#[pyfunction]
fn writer(filename:String, data:String) -> String {
	fs::write(filename.clone(), data).unwrap();
	return filename;
}

#[pyfunction]
fn creater(filename:String) -> String {
	fs::File::create(filename.clone()).unwrap();
	return filename;
}

#[pymodule]
fn binder(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(reader, m)?)?;
    m.add_function(wrap_pyfunction!(writer, m)?)?;
    m.add_function(wrap_pyfunction!(creater, m)?)?;
    Ok(())
}