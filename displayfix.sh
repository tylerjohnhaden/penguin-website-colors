#!/bin/sh

Xvfb :8 -screen 0 1024x768x24 &
export DISPLAY=":8"