import numpy as np
import cv2  
import os

class createNPZ:
    def __init__(self, images_dir):
        self.image_dir = images_dir
        self.image_filenames = sorted([f for f in os.listdir(images_dir) if f.endswith('.jpg') or f.endswith('.png')])
        # Set dummy focal length (adjust as needed)
        self.focal_length = 138.888 
        # Create a dummy rotation matrix (assuming all views are facing forward)
        self.rotation_matrix = np.eye(3)
        # Create a dummy translation vector (all views at the origin)
        self.translation_vector = np.zeros(3)
        self.num_images = len(self.image_filenames)
        self.poses = np.zeros((self.num_images, 4, 4), dtype=np.float64)  # 4x4 homogeneous transformation matrices, set dtype
        self.images = []

    def load_image(self, image_path):
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        return image.astype(np.float64)

    def generate(self, emit):
    # Fill the arrays with dummy data
        percent = 0
        for i, image_filename in enumerate(self.image_filenames):
            percent = (i + 1) / len(self.image_filenames) * 100
            if emit is not None:
                emit('progress', {'percent': percent, 'process': 'Creating Dataset'})
            image_path = os.path.join(self.image_dir, image_filename)
            image = self.load_image(image_path)  
            self.images.append(image) 
            translation_vector = self.translation_vector.reshape((3, 1))  # Reshape to (3, 1)
            pose = np.concatenate((self.rotation_matrix, translation_vector), axis=1)
            pose = np.vstack((pose, [0, 0, 0, 1]))  # Add the bottom row for homogeneity
            self.poses[i] = pose

    def save(self, output):
        data = {'images': np.array(self.images), 'poses': self.poses, 'focal': np.array(self.focal_length)}
        np.savez(output, **data)

    def generate_and_save(self, emit, output='/nerf_data.npz'):
        self.generate(emit);
        self.save(output)
        return 1, os.path.getsize(output) 