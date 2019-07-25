"""
Copyright (C) 2019 NVIDIA Corporation.  All rights reserved.
Licensed under the CC BY-NC-SA 4.0 license (https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode).
"""

import os
import time
import numpy as np
from collections import OrderedDict
import torchvision.transforms as transforms
from torchvision.utils import save_image

import data
from options.test_options import TestOptions
from models.pix2pix_model import Pix2PixModel
from util.visualizer import Visualizer
from util import html

opt = TestOptions().parse()

dataloader = data.create_dataloader(opt)

model = Pix2PixModel(opt)
model.eval()

visualizer = Visualizer(opt)

# create a webpage that summarizes the all results
web_dir = os.path.join(opt.results_dir, opt.name,
                       '%s_%s' % (opt.phase, opt.which_epoch))
webpage = html.HTML(web_dir,
                    'Experiment = %s, Phase = %s, Epoch = %s' %
                    (opt.name, opt.phase, opt.which_epoch))


def generate_noise(dim=512):
    # noise_vec = np.random.randint(0, 182, (dim, dim, 1))
    noise_vec = np.random.randint(0, 182, (dim, dim))
    transform_label = transforms.Compose([transforms.ToTensor()])
    label_tensor = transform_label(noise_vec)
    label_tensor = label_tensor.reshape((1, 1, dim, dim))

    return {
        'label': label_tensor,
        'instance': label_tensor,
        'image': label_tensor,
        'path': 'lol_5.jpg',
    }


# test
for i, data_i in enumerate(dataloader):
    if i * opt.batchSize >= opt.how_many:
        break

    new_data = generate_noise()
    print('generating image')
    print(new_data['label'])
    start = time.time()
    # generated = model(data_i, mode='inference')
    generated = model(new_data, mode='inference')
    save_image(generated, f'results/rand_{i}.jpg')
    print(generated)
    end = time.time()
    print('finished, took', end-start)

    # img_path = data_i['path']
    # for b in range(generated.shape[0]):
    #     print('process image... %s' % img_path[b])
    #     visuals = OrderedDict([('input_label', data_i['label'][b]),
    #                            ('synthesized_image', generated[b])])
    #     visualizer.save_images(webpage, visuals, img_path[b:b + 1])
    #
    # end = time.time()
    # print('other shit took', end - start)


webpage.save()
