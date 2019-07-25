# GAN Camera - generate frames from a gan like a camera
# Customized to work with a Roli Seaboard for shifting generation parameters
import os
import cv2
import time
import torch
import base64
import pickle
import json
import requests
import numpy as np
import torchvision.transforms as transforms
from torchvision.utils import save_image

from .base_camera import BaseCamera
from models.pix2pix_model import Pix2PixModel


def generate_noise(dim=256):
    # noise_vec = np.random.randint(0, 182, (dim, dim, 1))
    noise_vec = np.random.randint(0, 182, (dim, dim))
    transform_label = transforms.Compose([transforms.ToTensor()])
    label_tensor = transform_label(noise_vec)
    label_tensor = label_tensor.reshape((1, 1, dim, dim))
    # return label_tensor
    return {
        'label': label_tensor,
        'instance': label_tensor,
        'image': label_tensor,
        'path': 'lol_5.jpg',
    }


class GANModel:
    # img_fmt = dict(func=tflib.convert_images_to_uint8, nchw_to_nhwc=True)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    # gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.25)

    def __init__(self, opt):
        self.model = Pix2PixModel(opt)
        self.model.eval()

    def run_image(self, label_data: dict, as_bytes=True, i=1):
        # print(label_data['label'])
        generated = self.model(label_data, mode='inference')
        img = generated[0].mul_(255).add_(0.5).clamp_(0, 255).permute(1, 2, 0).to('cpu', torch.uint8).numpy()

        final_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # final_img = img

        if as_bytes:
            out_img = cv2.imencode('.jpg', final_img, self.encode_param)[1].tobytes()
        else:
            out_img = final_img
            # cv2.imwrite("face-" + str(i) + ".jpg", out_img)

        return out_img


class GANMera(BaseCamera):
    def __init__(self, opt, fps=90):
        self.framerate = 1 / fps
        self.opt = opt
        self.model = GANModel(opt)

        self.label_map = generate_noise()
        self.instance_map = generate_noise()
        # self.label_tensor = torch.from_numpy(self.label_map)
        self.label_tensor = self.label_map
        self.instance_tensor = self.instance_map
        self.last_frame = time.time()

        self.num_gen = 0
        super().__init__()

    def frames(self):
        while True:
            now = time.time()
            if abs(time.time() - self.last_frame) >= self.framerate:
                try:
                    label_data = requests.get('http://localhost:42069/label').json()
                    self.process_label_data(label_data)
                except requests.exceptions.ConnectionError:
                    # whoops the server is restarting
                    pass
                except json.decoder.JSONDecodeError:
                    # whoops the server reset in the middle of talking to me
                    pass
                yield self.get_image()
                self.last_frame = now

    def process_label_data(self, label_data=None):
        if not label_data:
            print('no label data, wtf')
            return

        label_map = label_data.get('label_map')
        if not label_map:
            print('where is my label map')
            return

        label_map_arr = np.array(label_map)
        label_map_shape = label_map_arr.shape
        self.label_map = label_map_arr.reshape((1, 1, *label_map_shape))
        self.label_tensor = torch.from_numpy(self.label_map)

        instance_map = label_data.get('instance_map')
        if instance_map:
            instance_map_arr = np.array(instance_map)
            instance_map_shape = instance_map_arr.shape
            self.instance_map = instance_map_arr.reshape((1, 1, *instance_map_shape))
            self.instance_tensor = torch.from_numpy(self.instance_map)

    def get_image(self):
        self.num_gen += 1
        print("Yo i've already generated like ", self.num_gen, "images for you bro")

        label_tensor = self.label_tensor
        label_data = {
            'label': label_tensor,
            'instance': self.instance_tensor,
            'image': label_tensor,
            'path': 'lol_5.jpg',
        }
        return self.model.run_image(label_data, i=self.num_gen)
