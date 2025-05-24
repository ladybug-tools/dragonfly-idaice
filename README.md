[![Build Status](https://github.com/ladybug-tools/dragonfly-idaice/workflows/CI/badge.svg)](https://github.com/ladybug-tools/dragonfly-idaice/actions)

[![Python 3.10](https://img.shields.io/badge/python-3.10-orange.svg)](https://www.python.org/downloads/release/python-3100/) [![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)

# dragonfly-idaice

Dragonfly extension for export to IES-VE GEM file format

## Installation
```console
pip install dragonfly-idaice
```

## QuickStart
```python
import dragonfly_idaice

```

## [API Documentation](http://ladybug-tools.github.io/dragonfly-idaice/docs)

## Local Development
1. Clone this repo locally
```console
git clone git@github.com:ladybug-tools/dragonfly-idaice

# or

git clone https://github.com/ladybug-tools/dragonfly-idaice
```
2. Install dependencies:
```console
cd dragonfly-idaice
pip install -r dev-requirements.txt
pip install -r requirements.txt
```

3. Run Tests:
```console
python -m pytest tests/
```

4. Generate Documentation:
```console
sphinx-apidoc -f -e -d 4 -o ./docs ./dragonfly_idaice
sphinx-build -b html ./docs ./docs/_build/docs
```
