#!/bin/bash

# Copyright (c) Microsoft Corporation - All rights reserved
# Licensed under the MIT License

BUILD_ROOT=build
mkdir -p $BUILD_ROOT
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/mnt/cache/xuekui/opt/miniconda3/envs/gpt-neox-genggui001-fp8 -B $BUILD_ROOT
cmake --build $BUILD_ROOT
cmake --install $BUILD_ROOT
