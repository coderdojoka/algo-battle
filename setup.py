from setuptools import setup, find_packages

__version__ = "0.1.1.post2"

install_requires = [
    "numpy>=1.16.2",
    "pandas>=0.24.2",
    "Pillow>=5.4.1",
    "PySide2>=5.12.2"
]

with open("README.md") as f:
    long_description = f.read()

setup(
    name="algo_battle",
    version=__version__,
    author="CoderDojo Karlsruhe, Lennart Hensler and Mark Weinreuter",
    author_email="coderdojo.karlsruhe@gmail.com",
    description="Educational Project to let different algorithms compete against each other. Currently only available in German.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Source": "https://github.com/coderdojoka/algo-battle"
    },
    install_requires=install_requires,
    python_requires=">=3.5",
    packages=find_packages(exclude=["test"]),
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: German",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Topic :: Education"
    ]
)
