import setuptools
import pathlib
import pkg_resources


setuptools.setup(
    name="dropi",
    version="1.0.0",
    author="Pedro Mora - \"drop\"",
    author_email="drop@42lisboa.com",
    description="A (small) api connector library for 42's intranet",
    long_description_content_type="text/markdown",
    url="https://github.com/42-Lisboa/dropi",
    project_urls={
        "Bug Tracker": "https://github.com/42-Lisboa/dropi/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    packages=['dropi'],
    python_requires=">=3.10",
    install_requires =["requests"]
)
