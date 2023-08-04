#!/bin/bash

if command -v python3.10 &>/dev/null; then
    echo "Python 3.10 is already installed."
else
    echo "Installing Python 3.10..."
    sudo apt update
    sudo apt install python3.10
fi

install_package() {
    package="$1"
    if python3.10 -m pip show "$package" &>/dev/null; then
        echo "Package $package is already installed."
    else
        echo "Installing $package..."
        python3.10 -m pip install "$package"
    fi
}

echo "Installing required packages..."
while read -r package; do
    install_package "$package"
done < requirements.txt

echo "Running the application..."
python3.10 main.py