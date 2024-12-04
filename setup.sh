#!/bin/bash

# Update and install Firefox
apt-get update
apt-get install -y firefox-esr

# Install geckodriver
curl -L https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz -o geckodriver.tar.gz
tar -xvzf geckodriver.tar.gz
mv geckodriver /usr/local/bin/

# Clean up
rm geckodriver.tar.gz
