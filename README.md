# Quality LAC data beta: Python validator
Python-side code for the Quality LAC Data Beta frontend

This is designed to work in tandem with the frontend, but can also be used as an individual package.

It provides methods of finding the validation errors defined by the DfE in 903 data.

### Project Structure

```
<to follow>
```


### Building a wheel for Pyodide

Pyodide requires a pure Python wheel - we can build this here. Clone the repo and move it into the directory. Then run

```
python setup.py bdist_wheel
```

### Local installation

To install, first clone the repo and move into the directory. Then run

```
pip install -e .
```