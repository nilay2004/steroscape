import numpy as np
from .fun__ import randomString
import time
import os
import matplotlib.pyplot as plt
import gc

import tensorflow as tf
tf.compat.v1.enable_eager_execution()


class NeRF:
    "FastNeRF class"
    def __init__(self, emit, checkProcessExecution, config, media_path, save_modal=True):
        self.save_modal= save_modal 
        self.media_path = media_path
        self.checkProcessExecution = checkProcessExecution
        self.emit = emit if emit is not None else lambda *args: None
        self.N_samples = 4
        self.L_embed = 1
        self.number_of_iterations = 100
        self.embed_fn = self.posenc
        self.images = []
        self.poses = []
        self.focal = 0
        self.H = 0
        self.W = 0
        self.modalDepth = 2
        self.modalWidth = 16
        self.images_len = 0
        self.testpose = []
        self.testimg = []
        self.output_video = f'/videos/vid-{randomString(8)}.mp4'
        self.video_size = 0
        self.generate_video = True 
        self.psnrs = []
        
        # Initialize input channel dimensions - MUST be defined before loading config
        self.in_ch_pos = 3 + 3 * 2 * self.L_embed  # Position encoding channels
        self.in_ch_dir = 0  # Direction encoding channels (not used in this version)
        
        # Update configuration if provided
        if config:
            if config.get('n_iterations'):
                self.number_of_iterations = config.get('n_iterations')
            if config.get('modal_depth'):
                self.modalDepth = config.get('modal_depth')
            if config.get('modal_width'):
                self.modalWidth = config.get('modal_width')
            if config.get('n_samples'):
                self.N_samples = config.get('n_samples')
        
        # Initialize model after all parameters are set
        self.model = self.init_model(D=self.modalDepth, W=self.modalWidth)
        self.clearResultsDir()
        # self.model = tf.keras.models.load_model('./models/mode.h5', compile=False)

    def saveModel(self, path):
        p = f"{path}{os.sep}saved_model"
        os.mkdir(p)
        tf.keras.models.save_model(self.model, p, save_format='tf')
        np.savez(f"{path}{os.sep}saved_model{os.sep}config.npz", H=self.H, W=self.W, focal=self.focal, testpose=self.testpose, N_samples=self.N_samples)
        return path

    def clearResultsDir(self):
        if os.path.exists('./results') and os.path.isdir('./results'):
            try:
                for root, dirs, files in os.walk('./results'):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            os.remove(file_path)
                        except OSError as e:
                            continue
            except OSError as e:
               pass 
        else:
            print(f"Directory not found")

    def loadDataset(self, path):
        try:
            print(f"Loading dataset from {path}")
            data = np.load(path)
            
            # Get data and ensure correct data types
            images = data['images']
            poses = data['poses']
            self.focal = np.float32(data['focal'])  # Ensure focal is float32
            
            print(f"Loaded data - Images shape: {images.shape}, dtype: {images.dtype}")
            print(f"Poses shape: {poses.shape}, dtype: {poses.dtype}")
            print(f"Focal: {self.focal}, type: {type(self.focal)}")
            
            # Resize images to reduce memory usage
            self.H, self.W = images.shape[1:3]
            
            # If images are too large, downsample them
            if self.H > 32 or self.W > 32:
                # Downsample to 32x32 to save even more memory
                new_H, new_W = 32, 32
                downsampled_images = []
                
                for img in images:
                    img_resized = tf.image.resize(img, [new_H, new_W])
                    downsampled_images.append(img_resized)
                
                images = tf.stack(downsampled_images)
                self.H, self.W = new_H, new_W
                print(f"Downsampled images to {new_H}x{new_W} to save memory")
            
            # Convert all arrays to float32 explicitly
            if images.dtype != np.float32:
                print(f"Converting images from {images.dtype} to float32")
                images = images.astype(np.float32)
                
            if poses.dtype != np.float32:
                print(f"Converting poses from {poses.dtype} to float32")
                poses = poses.astype(np.float32)
                
            self.images_len = len(images)
            
            if self.images_len < 2:
                raise ValueError("Not enough images in dataset (minimum 2 required)")
                
            self.testimg = images[self.images_len - 2]
            self.testpose = poses[self.images_len - 2]
            self.images = images[:self.images_len - 3,...,:3]
            self.poses = poses[:self.images_len - 3]
            
            # Ensure images are float32
            self.images = tf.cast(self.images, tf.float32)
            self.poses = tf.cast(self.poses, tf.float32)
            
            # Force garbage collection
            gc.collect()
            print("Dataset loaded successfully")
        except Exception as e:
            print(f"Error loading dataset: {e}")
            import traceback
            traceback.print_exc()
            raise

    def pose_spherical(self, theta, phi, radius):
        trans_t = lambda t : tf.convert_to_tensor([
            [1,0,0,0],
            [0,1,0,0],
            [0,0,1,t],
            [0,0,0,1],
        ], dtype=tf.float32)

        rot_phi = lambda phi : tf.convert_to_tensor([
            [1,0,0,0],
            [0,tf.cos(phi),-tf.sin(phi),0],
            [0,tf.sin(phi), tf.cos(phi),0],
            [0,0,0,1],
        ], dtype=tf.float32)

        rot_theta = lambda th : tf.convert_to_tensor([
            [tf.cos(th),0,-tf.sin(th),0],
            [0,1,0,0],
            [tf.sin(th),0, tf.cos(th),0],
            [0,0,0,1],
        ], dtype=tf.float32)
        c2w = trans_t(radius)
        c2w = rot_phi(phi/180.*np.pi) @ c2w
        c2w = rot_theta(theta/180.*np.pi) @ c2w
        c2w = np.array([[-1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1]]) @ c2w
        return c2w

    def Run(self):
        gc.collect()
        tf.keras.backend.clear_session()
        try:
            self.train()
        except (tf.errors.ResourceExhaustedError, MemoryError) as e:
            print(f"Memory error: {e}")
            self.emit('progress', {'message': f'Memory error: {e}', 'process': 'training', 'title': 'Error', 'progress': 0})
            gc.collect()
            tf.keras.backend.clear_session()
            return False

    def posenc(self, x):
        rets = [x]
        for i in range(self.L_embed):
            for fn in [tf.sin, tf.cos]:
                rets.append(fn(2.**i * x))
        return tf.concat(rets, -1) 

    def init_model(self, D=8, W=256):
        """
        Initialize the NeRF model with specified dimensions
        
        Args:
            D (int): Network depth, number of layers
            W (int): Network width, neurons per layer
            
        Returns:
            tf.keras.Model: Initialized model
        """
        tf.keras.backend.clear_session()  # Clear TF session to free memory
        gc.collect()  # Force garbage collection
        
        # Use the position encoding dimension as input shape
        input_shape = self.in_ch_pos
        inputs = tf.keras.Input(shape=(input_shape,))
        outputs = self.init_nerf_model(inputs, D, W)
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        return model

    def init_nerf_model(self, inputs, D=8, W=256):
        """
        Build the NeRF neural network structure
        
        Args:
            inputs: Input tensor
            D (int): Network depth
            W (int): Network width
            
        Returns:
            tf.Tensor: Output tensor
        """
        relu = tf.keras.layers.ReLU()
        dense = lambda W=W, act=relu : tf.keras.layers.Dense(W, activation=act)
        
        outputs = inputs
        for i in range(D):
            outputs = dense()(outputs)
            if i%4==0 and i>0:
                outputs = tf.concat([outputs, inputs], -1)
        outputs = dense(4, act=None)(outputs)
        
        return outputs

    def get_rays(self, H, W, focal, c2w):
        i, j = tf.meshgrid(tf.range(W, dtype=tf.float32), tf.range(H, dtype=tf.float32), indexing='xy')
        dirs = tf.stack([(i-W*.5)/focal, -(j-H*.5)/focal, -tf.ones_like(i)], -1)
        rays_d = tf.reduce_sum(dirs[..., np.newaxis, :] * c2w[:3,:3], -1)
        rays_o = tf.broadcast_to(c2w[:3,-1], tf.shape(rays_d))
        return rays_o, rays_d

    def render_rays(self, network_fn, rays_o, rays_d, near, far, N_samples, rand=False):
        def batchify(fn, chunk=128):  # Reduced further from 256 to 128
            return lambda inputs : tf.concat([fn(inputs[i:i+chunk]) for i in range(0, inputs.shape[0], chunk)], 0)

        # Compute 3D query points
        N_samples = tf.cast(tf.minimum(N_samples, 4), tf.int32)  # Ensure maximum of 4 samples and it's an integer
        
        z_vals = tf.linspace(near, far, N_samples)
        if rand:
            # Ensure shape calculation is done with tensor operations
            shape = tf.concat([tf.shape(rays_o)[:-1], [N_samples]], axis=0)
            # Create random tensor with proper shape
            noise = tf.random.uniform(shape=shape) * (far-near)/tf.cast(N_samples, tf.float32)
            z_vals = z_vals + noise
        
        # Ensure all tensors have the same data type
        rays_o = tf.cast(rays_o, tf.float32)
        rays_d = tf.cast(rays_d, tf.float32)
        z_vals = tf.cast(z_vals, tf.float32)
        
        # Continue with the existing code
        pts = rays_o[...,None,:] + rays_d[...,None,:] * z_vals[...,:,None]

        # Run network
        pts_flat = tf.reshape(pts, [-1,3])
        # pts_flat = self.embed_fn(pts_flat)
        pts_flat = self.posenc(pts_flat)
        raw = batchify(network_fn)(pts_flat)
        raw = tf.reshape(raw, list(pts.shape[:-1]) + [4])
        # Compute opacities and colors
        sigma_a = tf.nn.relu(raw[...,3])
        rgb = tf.math.sigmoid(raw[...,:3])
        # Do volume rendering
        dists = tf.concat([z_vals[..., 1:] - z_vals[..., :-1], tf.broadcast_to([1e10], z_vals[...,:1].shape)], -1)
        alpha = 1.-tf.exp(-sigma_a * dists)
        weights = alpha * tf.math.cumprod(1.-alpha + 1e-10, -1, exclusive=True)

        rgb_map = tf.reduce_sum(weights[...,None] * rgb, -2)
        depth_map = tf.reduce_sum(weights * z_vals, -1)
        acc_map = tf.reduce_sum(weights, -1)

        return rgb_map, depth_map, acc_map

    def render(self, H, W, focal, chunk=512, rays=None, c2w=None, ndc=True,
               near=0., far=1., use_viewdirs=False, c2w_staticcam=None):
        gc.collect()  # Force garbage collection before rendering
        
        # Reduce chunk size for lower memory usage
        chunk = 256  # Smaller chunk size to reduce memory consumption
        
        # If we're given rays directly, use those
        if rays is not None:
            # Make all directions unit magnitude
            # ray_batch = rays_o, rays_d = rays[:, 0:3], rays[:, 3:6]  # [N_rays, 3] each
            # viewdirs = rays[:, -3:] if rays.shape[-1] > 8 else None
            # sh = rays_d.shape
            # try:
            #     rays_o, rays_d = rays
            # except:
            #     print('ERROR WHILE TRYING TO UNPACK RAYS')
            #     print('rays.shape', rays.shape)
            #     print('rays', rays)
            #     raise
            rays_o, rays_d = rays
            
            if use_viewdirs:
                viewdirs = rays_d
    
            # Provide ray directions as input
            sh = rays_d.shape
            rays_d = tf.reshape(rays_d, [-1, 3])
            rays_o = tf.reshape(rays_o, [-1, 3])
            
            # Create ray batch
            rays_o = tf.cast(rays_o, dtype=tf.float32)
            rays_d = tf.cast(rays_d, dtype=tf.float32)
    
            # Implement batched rendering with explicit memory management
            all_ret = {}
            for i in range(0, rays_o.shape[0], chunk):
                gc.collect()  # Force garbage collection each batch
                ret = self.render_rays(self.model,
                                  rays_o[i:i+chunk],
                                  rays_d[i:i+chunk],
                                  near,
                                  far,
                                  N_samples=16,  # Reduced samples
                                  rand=False)
                for k in ret:
                    if k not in all_ret:
                        all_ret[k] = []
                    all_ret[k].append(ret[k])
            
            all_ret = {k: tf.concat(all_ret[k], 0) for k in all_ret}
            for k in all_ret:
                k_sh = list(sh[:-1]) + list(all_ret[k].shape[1:])
                all_ret[k] = tf.reshape(all_ret[k], k_sh)
    
            del rays_o, rays_d
            gc.collect()
            
            return all_ret