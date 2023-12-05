#!/bin/bash

# Copyright (c) Microsoft Corporation - All rights reserved
# Licensed under the MIT License

BUILD_ROOT=build
mkdir -p $BUILD_ROOT

echo "install in to "$PREFIX

cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=$PREFIX -B $BUILD_ROOT
cmake --build $BUILD_ROOT
cmake --install $BUILD_ROOT
