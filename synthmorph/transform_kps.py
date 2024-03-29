"""Transforms keypoints using the negative flow field
and computes the TRE between the transformed keypoints and the fixed ones
before and after registration
."""

import os
import numpy as np
import nibabel as nib
from voxelmorph.torch.networks import VxmDense
from nibabel.processing import conform
import torch
import pandas as pd
from voxelmorph.tf.utils import point_spatial_transformer
import tensorflow as tf
from utils import compute_TRE

CASE = 'case_004'

# Load preprocessed data (scaled between 0 and 1 and with the moving data in the space of the fixed one)
fixed = nib.load(f"processed_data/copd_scans/scans/{CASE}_insp.nii.gz")
fixed_a = fixed.get_fdata()
moving = nib.load(f"processed_data/copd_scans/scans/{CASE}_exp.nii.gz")
moving_a = moving.get_fdata()
kps = pd.read_csv(f"processed_data/copd_scans/keypoints/{CASE}.csv", header=None).values

    
moving_kps = kps[:, [0, 1, 2]]
fixed_kps = kps[:, [3, 4, 5]]

pos_flow = np.load(f"synthmorph/results/{CASE}_pos_flow.npy")
neg_flow = np.load(f"synthmorph/results/{CASE}_neg_flow.npy")

print(kps)

# # print(moving.shape, moving.max(), moving.min())
# # These data are in my local computer but any data could be used to perform the same analysis.
# # It only needs to be scaled and set in a common space

# Load the PyTorch model and specify the device
pt_model_inference = torch.load('/home/mira1/vlex_mira/maia-mira/models/weights/torch_shapes.pt')
pt_model_inference.eval()

# # Prepare the data for inference
# data_moving = np.expand_dims(moving.get_fdata().squeeze(), axis=(0, -1)).astype(np.float32)
# data_fixed = np.expand_dims(fixed.get_fdata().squeeze(), axis=(0, -1)).astype(np.float32)

# # Set up tensors and permute for inference
# input_moving = torch.from_numpy(data_moving).to(device).float().permute(0, 4, 1, 2, 3)
# input_fixed = torch.from_numpy(data_fixed).to(device).float().permute(0, 4, 1, 2, 3)

annotations = moving_kps[:, [0, 1, 2]]
annotations = annotations[np.newaxis, ...]

# print(neg_flow.shape)
neg_flow_reshaped = np.moveaxis(neg_flow, [1], [4])
# print(neg_flow_reshaped.shape)
# warp annotations
data = [tf.convert_to_tensor(f, dtype=tf.float32) for f in [annotations, neg_flow_reshaped]]
moving_transformed = point_spatial_transformer(data)[0, ...].numpy()

if 'case_001' in CASE:
    # voxel_size = [0.63, 0.63, 3.16] # gets size (512, 512, 96)
    voxel_size = [1.44, 1.44, 3.14] # gets size (224, 224, 96)
elif 'case_002' in CASE:
    # voxel_size = [0.65, 0.65, 2.65]
    voxel_size = [1.489, 1.489, 2.65]
elif 'case_003' in CASE:
    # voxel_size = [0.65, 0.65, 3.29]
    voxel_size = [1.489, 1.489, 3.29]
elif 'case_004' in CASE:
    # voxel_size = [0.59, 0.59, 3.29]
    voxel_size = [1.35, 1.35, 3.29]

print('Before: ', compute_TRE(moving_kps, fixed_kps, voxel_size))
print('After: ', compute_TRE(moving_transformed, fixed_kps, voxel_size))