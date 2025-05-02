import os
import numpy as np
import imghdr
from PIL import Image
from scipy.spatial.transform import Rotation
import glob 
import traceback

class setupDataset:
    def __init__(self, images_dir, use_colmap_output, emit):
        self.emit = emit if emit is not None else lambda *args: None
        self.project_path = f"{os.getenv('colmap')}"
        self.cameras = self.project_path + 'cameras.txt'
        self.images = self.project_path + 'images.txt'
        self.output_npz = os.path.join(images_dir,  'dataset.npz')
        self.output_size = 0
        self.images_dir = images_dir 
        self.total_tasks = 0
        self.obtain_tasks = 0
        self.def_pose = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)  # Explicitly set dtype for poses
        self.def_focal = np.array(800, dtype=np.float32)
        
        if use_colmap_output:
            self.create_npz_using_colmap(self.cameras, self.images, self.images_dir, self.output_npz)
        else:
            self.generate()
        try: 
            os.unlink(self.cameras)
            os.unlink(self.images)
        except Exception as e:
            pass
    
    def isDatasetCreated(self):
        return os.path.exists(self.output_npz)
    
    def read_cameras(self, cameras_txt_path):
        cameras = {}
        with open(cameras_txt_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line[0] == '#':
                    continue 
                data = line.strip().split()
                if len(data) < 5:
                    continue 
                camera_id = int(data[0])
                focal_length = float(data[4])
                cameras[camera_id] = focal_length
        return cameras

    def read_poses(self, images_txt_path):
        poses = {}
        with open(images_txt_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if '.jpg' not in line:
                    continue
                if line[0] == '#':
                    continue  
                data = line.strip().split()
                if len(data) < 10:
                    continue  
                if '.' in data[0]:
                    image_id = float(data[0])
                else:
                    image_id = int(data[0])
                qw, qx, qy, qz = map(float, data[1:5])
                tx, ty, tz = map(float, data[5:8])
                image_name = data[9]
                rotation_matrix = Rotation.from_quat(np.array([qw, qx, qy, qz])).as_matrix()
                pose_matrix = np.eye(4, dtype=np.float32)  # Explicitly set dtype
                pose_matrix[:3, :3] = rotation_matrix
                pose_matrix[:, 3] = [tx, ty, tz, 1]
                poses[f'{image_id}-{image_name}'] = {
                    'quaternion': pose_matrix,
                    'image_name': image_name
                }
        return poses

    def load_images(self, image_dir):
        images = []
        i = 0
        files_list = []

        # Look for both JPG and PNG files
        jpg_files = glob.glob(os.path.join(image_dir, '*.jpg'))
        png_files = glob.glob(os.path.join(image_dir, '*.png'))
        files_list = jpg_files + png_files
        
        # Ensure we have files
        if not files_list:
            print(f"No image files found in {image_dir}")
            print(f"Directory contents: {os.listdir(image_dir)}")
            return images
            
        try:
            # Sort by filename number
            files_list = sorted(files_list, key=lambda x: int(os.path.basename(x).split('.')[0]))
        except:
            # Fallback sorting if filename isn't a number
            files_list = sorted(files_list)
            
        print(f"Found {len(files_list)} files to process: {files_list}")
        
        for file in files_list:
            try:
                print(f"Processing image file: {file}")
                # Ensure images are explicitly float32
                image = np.array(Image.open(file).convert('RGB'), dtype=np.float32) / 255.0
                images.append([os.path.basename(file), image])
                print(f"Successfully loaded {file}")
            except Exception as e:
                print(f"Error loading image {file}: {e}")
        
        return images

    def create_npz_using_colmap(self, cameras_txt_path, images_txt_path, image_dir, output_npz_path):
        try:
            self.emit('progress', {'progress': 0, 'process': 'generating_npz', 'title': "Creating dataset..."})
            cameras = self.read_cameras(cameras_txt_path)
            poses = self.read_poses(images_txt_path)
            poses_keys = poses.keys()
            nposes = []
            images = self.load_images(self.images_dir)
            
            if not images:
                print("No images found. Cannot create dataset.")
                self.emit('progress', {'progress': 0, 'process': 'generating_npz', 'title': "Error: No images found", 'message': "No images found in directory"})
                return
                
            nimages = [image[1] for image in images]
            
            # Convert focal length to float32
            if cameras and sorted(cameras.keys()):
                focal_lengths = np.float32(np.max([cameras[cam_id] for cam_id in sorted(cameras.keys())]))
            else:
                focal_lengths = self.def_focal
                
            i = 0
            for image in images:
                n = image[0] #iterated image name 
                poses_data_found = False 
                i = i + 1
                for key in poses_keys:
                    img_name = key.split('-')[1]
                    if img_name == n:
                        nposes.append(poses[key]['quaternion'])
                        poses_data_found = True
                        break
                if poses_data_found == False: 
                    nposes.append(self.def_pose)
            
            # Convert images to a proper numpy array with correct dtype
            try:
                # First check if nimages is empty
                if not nimages:
                    raise ValueError("No valid images found in the directory")
                
                # Check if all images are the same shape
                shapes = [img.shape for img in nimages]
                if not all(shape == shapes[0] for shape in shapes):
                    print(f"Warning: Images have different shapes: {shapes}")
                    # Resize all to the first image's shape if needed
                    first_shape = shapes[0]
                    for i in range(1, len(nimages)):
                        if shapes[i] != first_shape:
                            from skimage.transform import resize
                            nimages[i] = resize(nimages[i], first_shape, preserve_range=True).astype(np.float32)
                
                # Create numpy array
                nimages_array = np.array(nimages, dtype=np.float32)
                
                # Ensure poses are correct shape and type
                poses_array = np.array(nposes, dtype=np.float32)
                
                # Print debug info
                print(f"Images array shape: {nimages_array.shape}, dtype: {nimages_array.dtype}")
                print(f"Poses array shape: {poses_array.shape}, dtype: {poses_array.dtype}")
                print(f"Focal length: {focal_lengths}, type: {type(focal_lengths)}")
                
                # Save with explicit types
                np.savez(output_npz_path, 
                        focal=focal_lengths, 
                        poses=poses_array, 
                        images=nimages_array)
                print(f"Successfully created dataset at {output_npz_path}")
            except Exception as e:
                print(f"Error processing or saving dataset: {e}")
                traceback.print_exc()
                self.emit('progress', {'progress': 0, 'process': 'generating_npz', 'title': "Error processing images", 'message': str(e)})
                return
    
            self.emit('progress', {'progress': 100, 'process': 'generating_npz', 'title': "Dataset created successfully"})
            self.output_size = os.path.getsize(output_npz_path)
        except Exception as e:
            print(f"Error in create_npz_using_colmap: {e}")
            traceback.print_exc()
            self.emit('progress', {'progress': 0, 'process': 'generating_npz', 'title': "Error creating dataset", 'message': str(e)})

    def generate(self):
        try:
            print(f"Generating dataset with default poses, output to {self.output_npz}")
            # Create directory if needed
            output_dir = os.path.dirname(self.output_npz)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Get files and create dataset
            image_files = self.load_images(self.images_dir)
            print(f"Found {len(image_files)} images in {self.images_dir}")
            
            if len(image_files) < 1:
                print("Error: No images found")
                self.emit('progress', {'progress': 0, 'process': 'generating_npz', 'title': "Error: No images found", 'message': "No images found in directory"})
                return
            
            files = [file[1] for file in image_files]
            poses = [self.def_pose] * len(files)
            
            # Check if all images are the same shape
            shapes = [img.shape for img in files]
            if not all(shape == shapes[0] for shape in shapes):
                print(f"Warning: Images have different shapes: {shapes}")
                # Resize all to the first image's shape if needed
                first_shape = shapes[0]
                for i in range(1, len(files)):
                    if shapes[i] != first_shape:
                        from skimage.transform import resize
                        files[i] = resize(files[i], first_shape, preserve_range=True).astype(np.float32)
            
            # Ensure images are numpy arrays with the correct dtype
            try:
                files_array = np.array(files, dtype=np.float32)
                poses_array = np.array(poses, dtype=np.float32)
                
                # Print debug info
                print(f"Images array shape: {files_array.shape}, dtype: {files_array.dtype}")
                print(f"Poses array shape: {poses_array.shape}, dtype: {poses_array.dtype}")
                print(f"Focal length: {self.def_focal}, type: {type(self.def_focal)}")
                
                # Save the dataset with explicit type conversion
                np.savez(self.output_npz, 
                        focal=self.def_focal, 
                        poses=poses_array, 
                        images=files_array)
                print(f"Successfully created dataset at {self.output_npz}")
                self.emit('progress', {'progress': 100, 'process': 'generating_npz', 'title': "Creating dataset with default poses"})
            except Exception as e:
                print(f"Error saving dataset: {e}")
                traceback.print_exc()
                self.emit('progress', {'progress': 0, 'process': 'generating_npz', 'title': "Error saving dataset", 'message': str(e)})
        except Exception as e:
            print(f"Error generating dataset: {e}")
            traceback.print_exc()
            self.emit('progress', {'progress': 0, 'process': 'generating_npz', 'title': "Error creating dataset", 'message': str(e)})

# if __name__ == '__main__':
#     os.environ['colmap'] = f'{os.getcwd()}\\colmap\\'
#     def emit(*args):
#         return
#     setupDataset('F:\\final_year\\backend\\media\\test', True, emit)
#     data = np.load('F:\\final_year\\backend\\media/test/dataset.npz')
#     poses = data['poses']
#     i = 0
#     for img in poses:
#         i = i + 1
#         print(i, ' => ', img)