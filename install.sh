#!/bin/bash

NCCL_HOME="/mnt/cache/xuekui/opt/miniconda3/envs/gpt-neox-genggui001-fp8"
MPC_HOME="/mnt/petrelfs/share/gcc/mpc-0.8.1"
MPFR_HOME="/mnt/petrelfs/share/gcc/mpfr-2.4.2"
GMP_HOME="/mnt/petrelfs/share/gcc/gmp-4.3.2"
MPI_HOME="/mnt/petrelfs/share/openmpi"

export NCCL_HOME=$NCCL_HOME
export CPLUS_INCLUDE_PATH=$CPLUS_INCLUDE_PATH:$NCCL_HOME/include:$MPC_HOME/include:$MPFR_HOME/include:$GMP_HOME/include:$MPI_HOME/include
export C_INCLUDE_PATH=$C_INCLUDE_PATH:$NCCL_HOME/include:$MPC_HOME/include:$MPFR_HOME/include:$GMP_HOME/include:$MPI_HOME/include
export LIBRARY_PATH=$LIBRARY_PATH:$NCCL_HOME/lib:$MPC_HOME/lib:$MPFR_HOME/lib:$GMP_HOME/lib:$MPI_HOME/lib
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$NCCL_HOME/lib:$MPC_HOME/lib:$MPFR_HOME/lib:$GMP_HOME/lib:$MPI_HOME/lib
export NCCL_ROOT_DIR=$NCCL_HOME
export NCCL_INCLUDE_DIR=$NCCL_HOME/include
export NCCL_LIB_DIR=$NCCL_HOME/lib
# export NCCL_VERSION=2
# export NCCL_LAUNCH_MODE=GROUP

export PATH="/mnt/petrelfs/share/gcc/gcc-9.3.0/bin:$MPI_HOME/bin:$PATH" 
export CUDA_HOME="/mnt/cache/xuekui/opt/miniconda3/envs/gpt-neox-genggui001-fp8" 
export PREFIX="/mnt/cache/xuekui/opt/miniconda3/envs/gpt-neox-genggui001-fp8"
export TORCH_CUDA_ARCH_LIST="7.0 7.5 8.0 8.6 9.0"
# cd third_party/msccl

# make -j 32 src.build NVCC_GENCODE="\
#     -gencode=arch=compute_70,code=sm_70 \
#     -gencode=arch=compute_80,code=sm_80 \
#     -gencode=arch=compute_90,code=sm_90"

# make src.install

pip install .
make postinstall
