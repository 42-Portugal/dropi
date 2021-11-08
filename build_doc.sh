#!/bin/bash
set -e
sphinx-apidoc -f -o docs/source dropi -H dropi
make html -C docs
echo "you can visit the documentation locally at file://$(pwd)/docs/build/html/index.html (CTRL + Click to go directly there ;) )"
