import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dropi",
    version="0.42",
    author="Pedro Mora - \"drop\"",
    author_email="drop@42lisboa.com",
    description="A (small) 42 api connector library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/42-Lisboa/dropi",
    project_urls={
        "Bug Tracker": "https://github.com/42-Lisboa/dropi/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.9",
)
