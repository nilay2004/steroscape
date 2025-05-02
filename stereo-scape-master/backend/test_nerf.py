import os
import numpy as np
from utils.nerf import NeRF

def mock_emit(event, data):
    print(f"[{event}] {data}")

def mock_check():
    return False

# Create test directory if it doesn't exist
test_dir = os.path.join(os.getcwd(), 'test_data')
if not os.path.exists(test_dir):
    os.makedirs(test_dir)

# Initialize the NeRF model with minimal settings
config = {
    'n_iterations': 10,  # Small number for quick test
    'modal_depth': 4,
    'modal_width': 128,
    'n_samples': 32
}

print("Initializing NeRF model...")
nerf = NeRF(emit=mock_emit, 
            checkProcessExecution=mock_check, 
            config=config, 
            media_path=test_dir, 
            save_modal=False)

# Create a simple dataset
print("Creating test dataset...")
H, W = 100, 100  # Small image dimensions for testing
testimg = np.ones((H, W, 3), dtype=np.float32)  # White image
focal = 100
# Create 3 test images
images = np.stack([testimg] * 3)
# Create simple poses (identity transforms)
poses = np.stack([np.eye(4)] * 3)

print("Setting up test data...")
# Manually set the properties
nerf.H = H
nerf.W = W
nerf.focal = focal
nerf.images = images
nerf.poses = poses
nerf.testimg = testimg
nerf.testpose = np.eye(4)

print("Starting test run...")
# Try to run the model
try:
    nerf.Run()
    print("✅ Test passed: NeRF model runs successfully!")
except Exception as e:
    print(f"❌ Test failed: {e}")
    raise e 