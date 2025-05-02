import os
import cv2
import numpy as np
import tensorflow as tf
from utils.fun__ import randomString
from .nerf import NeRF
import matplotlib.pyplot as plt
tf.compat.v1.enable_eager_execution()


class LoadNeRF(NeRF):
    def __init__(self, media_path, emit=lambda x: x, use_emit=None):
        self.use_emit = use_emit
        self.emit = emit
        self.media_path = media_path
        self.model_path = f'{os.getcwd()}/media/{media_path}/saved_model/'
        self.loaded_model = tf.keras.models.load_model(self.model_path)
        self.L_embed = 6
        self.output_video = f'/videos/vid-{randomString(8)}.mp4'
        config = np.load(f'{self.model_path}config.npz')
        self.H = config['H']
        self.W = config['W']
        self.focal = config['focal']
        self.testpose = config['testpose']
        self.N_samples = config['N_samples']

    def getView(self, the=90, pi=0.8, rad=0.2, prevImg=""):
        c2w = self.pose_spherical(the, pi, rad)
        rays_o, rays_d = self.get_rays(self.H, self.W, self.focal, c2w) 
        rgb, depth, acc = self.render_rays(self.loaded_model, rays_o, rays_d, near=2., far=6., N_samples=self.N_samples)
        img = f'/media/{self.media_path}/__{randomString(5)}.jpg'
        plt.imsave(os.getcwd() + img, rgb.numpy())
        if prevImg != "":
            os.remove(os.getcwd() + prevImg)
        return img
    

    def Video360(self, video_path=''):
        video_path = video_path if video_path != '' else self.output_video
        frames = []
        prcnt = 0
        i = 0
        for th in np.linspace(0., 360., 120, endpoint=False):
            i += 1
            prcnt = i / 360 * 300
            c2w = self.pose_spherical(th, -30., 4.)
            rays_o, rays_d = self.get_rays(self.H, self.W, self.focal, c2w[:3,:4])
            rgb, depth, acc = self.render_rays(self.loaded_model, rays_o, rays_d, near=2., far=6., N_samples=self.N_samples)
            frames.append((255*np.clip(rgb,0,1)).astype(np.uint8))
            if self.use_emit:
                self.emit('progress', {'process': 'generating_video', 'title': 'Generating 360 video', 'progress': prcnt})
        
        fourcc = cv2.VideoWriter_fourcc(*'X264')
        width, height = frames[0].shape[:2]
        video = cv2.VideoWriter(os.getcwd() + video_path, fourcc=fourcc, fps=30, frameSize=(width, height))
        for f in frames:
            video.write(f)
        video.release()
        # video_size = os.path.getsize(os.getcwd() + video_path)
        return video_path


