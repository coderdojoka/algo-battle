from setuptools import setup, find_packages

__version__ = "0.1.0"

install_requires = [
    "numpy>=1.16.2",
    "pandas>=0.24.2",
    "Pillow>=5.4.1",
    "PySide2>=5.12.2",
    "PyYAML>=5.1"
]

setup(
    name="algo_battle",
    version=__version__,
    install_requires=install_requires,
    packages=find_packages(),
    zip_safe=False
)
