# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Tests for deepspeed engine with MS-AMP."""

import unittest

import torch
import torch.nn as nn
from deepspeed.ops.adam import FusedAdam
from deepspeed.runtime.fp16.fused_optimizer import FP16_Optimizer

from msamp import deepspeed
from msamp.common.dtype.dtypes import Dtypes
from msamp.optim import LBAdam, LBAdamW, DSAdam
from msamp.deepspeed.runtime.engine import split_half_float_double_sparse
from msamp.deepspeed.runtime.fp8.fused_optimizer import FP8Optimizer
from msamp.nn import LinearReplacer
from tests.helper import decorator


class DeepSpeedEngineTestCase(unittest.TestCase):
    """Test MSAMPDeepSpeedEngine."""
    def setUp(self):
        """Hook method for setting up the test fixture before exercising it."""
        torch.manual_seed(1000)

    def tearDown(self):
        """Hook method for deconstructing the test fixture after testing it."""
        pass

    @decorator.cuda_test
    def test_split_half_float_double_sparse(self):
        """Test split_half_float_double_sparse method."""
        tensors = []

        dtype_list = [torch.float32, torch.float16, torch.float64, torch.bfloat16]

        size_list = [3, 4, 5, 6]

        for i, size in enumerate(size_list):
            for _ in range(size):
                tensor = torch.randn(2, 2, dtype=dtype_list[i], device='cuda')
                tensors.append(tensor)

        num_scaling_tensor = 7
        for i in range(num_scaling_tensor):
            tensor = torch.randn(2, 2, dtype=torch.float32, device='cuda').cast(Dtypes.kfloat8_e4m3)
            tensors.append(tensor)
        buckets = split_half_float_double_sparse(tensors)

        assert len(buckets) == 5

        has_scaling_tensor = False
        for dtype, bucket in buckets:
            if dtype == 'msamp.common.tensor.tensor.ScalingTensor':
                assert len(bucket) == num_scaling_tensor
                has_scaling_tensor = True
        assert has_scaling_tensor

    @decorator.cuda_test
    def test_config_optimizer(self):
        """Test config optimizer."""
        model = nn.Linear(4, 4, device='cuda')

        # Don't specify optimizer in config.
        config = {
            'train_batch_size': 1,
        }
        model1, _, _, _ = deepspeed.initialize(model=model, config=config)
        assert model1.basic_optimizer is None
        assert model1.optimizer is None

        # adam + FP32.
        config = {
            'train_batch_size': 1,
            'optimizer': {
                'type': 'adam',
            }
        }

        model2, _, _, _ = deepspeed.initialize(model=model, config=config)
        assert isinstance(model2.basic_optimizer, FusedAdam)
        assert model2.basic_optimizer == model2.optimizer

        # adam + FP16.
        config = {
            'train_batch_size': 1,
            'optimizer': {
                'type': 'adam'
            },
            'fp16': {
                'enabled': True,
            }
        }

        model3, _, _, _ = deepspeed.initialize(model=model, config=config)
        assert isinstance(model3.basic_optimizer, FusedAdam)
        assert isinstance(model3.optimizer, FP16_Optimizer)

        # DSAdam
        config = {
            'train_batch_size': 1,
            'optimizer': {
                'type': 'msamp_adam',
            }
        }
        model4, _, _, _ = deepspeed.initialize(model=model, config=config)

        assert isinstance(model4.basic_optimizer, DSAdam)
        assert isinstance(model4.optimizer, FP8Optimizer)

        # LBAdam
        config = {
            'train_batch_size': 1,
            'optimizer': {
                'type': 'msamp_adam',
                'params': {
                    'torch_adam': True,
                    'adam_w_mode': False,
                }
            }
        }

        model5, _, _, _ = deepspeed.initialize(model=model, config=config)

        assert isinstance(model5.basic_optimizer, LBAdam)
        assert isinstance(model5.optimizer, FP8Optimizer)

        # LBAdamW
        config = {
            'train_batch_size': 1,
            'optimizer': {
                'type': 'msamp_adamw',
                'params': {
                    'torch_adam': True,
                }
            }
        }

        model6, _, _, _ = deepspeed.initialize(model=model, config=config)

        assert isinstance(model6.basic_optimizer, LBAdamW)
        assert isinstance(model6.optimizer, FP8Optimizer)

    @decorator.cuda_test
    def test_backward(self):
        """Test backward method."""
        model = nn.Linear(4, 4, device='cuda')
        model = LinearReplacer.replace(model, Dtypes.kfloat16)
        optimizer = LBAdamW(list(model.parameters()))

        config = {
            'train_batch_size': 1,
        }
        model, optimizer, _, _ = deepspeed.initialize(model=model, optimizer=optimizer, config=config)

        inputs = []
        num_inputs = 10
        for _ in range(num_inputs):
            inputs.append(torch.rand(4, 4, device='cuda'))

        losses = []
        epoches = 10
        for _ in range(epoches):
            loss = 0
            for i in range(num_inputs):
                output = model(inputs[i])
                loss += output.sum()
                model.backward(loss)
                model.step()
            loss /= 10
            losses.append(loss)

        for i in range(epoches):
            if i > 0:
                assert losses[i] < losses[i - 1]