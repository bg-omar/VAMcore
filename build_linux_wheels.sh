#!/bin/bash
# Script to build Linux wheels using Docker (manylinux)
# This is an alternative to GitHub Actions for local building

set -e

VERSION="0.1.0"
PYTHON_VERSIONS=("cp37" "cp38" "cp39" "cp310" "cp311" "cp312" "cp313")

echo "Building Linux wheels for swirl-string-core ${VERSION}"

# Create dist directory
mkdir -p dist

# Build for each Python version
for PYTHON in "${PYTHON_VERSIONS[@]}"; do
    echo "Building for Python ${PYTHON}..."
    
    # Use manylinux2014 (compatible with most Linux distributions)
    docker run --rm -v "$(pwd):/io" quay.io/pypa/manylinux2014_x86_64 bash -c "
        # Install Python
        /opt/python/${PYTHON}-${PYTHON}/bin/pip install --upgrade pip
        /opt/python/${PYTHON}-${PYTHON}/bin/pip install build wheel setuptools pybind11 numpy
        
        # Build wheel
        cd /io
        /opt/python/${PYTHON}-${PYTHON}/bin/python -m build --wheel
        
        # Fix wheel tags (auditwheel)
        /opt/python/${PYTHON}-${PYTHON}/bin/pip install auditwheel
        for wheel in dist/*.whl; do
            if [[ \$wheel == *linux_* ]]; then
                auditwheel repair \$wheel -w dist/
                rm \$wheel
            fi
        done
    "
done

echo "Build complete! Wheels are in dist/"
ls -lh dist/*.whl


