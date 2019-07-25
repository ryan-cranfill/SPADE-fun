import string
import imageio
import requests
from flask_cors import CORS
from flask import Flask, Response, request, jsonify, url_for

from gan_camera import GANMera
from options.test_options import TestOptions

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'secret!'

# opt = TestOptions()
# --dataset_mode coco --dataroot datasets/coco_stuff --gpu_ids -1 --how_many 3
# opt = opt.parse()
# opt.name = 'coco_pretrained'
# opt.dataset_mode = 'coco'
# opt.dataroot = 'datasets/coco_stuff'
opt = TestOptions().parse()
gan = GANMera(opt)


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    global gan
    return Response(gen(gan),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=42042)
#
# import os
# import time
# import requests
# import numpy as np
# from collections import OrderedDict
# import torchvision.transforms as transforms
# from torchvision.utils import save_image
#
# import data
# from options.test_options import TestOptions
# from models.pix2pix_model import Pix2PixModel
# from util.visualizer import Visualizer
# from util import html
#
# opt = TestOptions().parse()
#
# dataloader = data.create_dataloader(opt)
#
# model = Pix2PixModel(opt)
# model.eval()
#
# visualizer = Visualizer(opt)
#
# # create a webpage that summarizes the all results
# web_dir = os.path.join(opt.results_dir, opt.name,
#                        '%s_%s' % (opt.phase, opt.which_epoch))
# webpage = html.HTML(web_dir,
#                     'Experiment = %s, Phase = %s, Epoch = %s' %
#                     (opt.name, opt.phase, opt.which_epoch))
#
#
# def generate_noise(dim=512):
#     # noise_vec = np.random.randint(0, 182, (dim, dim, 1))
#     noise_vec = np.random.randint(0, 182, (dim, dim))
#     transform_label = transforms.Compose([transforms.ToTensor()])
#     label_tensor = transform_label(noise_vec)
#     label_tensor = label_tensor.reshape((1, 1, dim, dim))
#
#     return {
#         'label': label_tensor,
#         'instance': label_tensor,
#         'image': label_tensor,
#         'path': 'lol_5.jpg',
#     }
#
#
# # test
# for i, data_i in enumerate(dataloader):
#     if i * opt.batchSize >= opt.how_many:
#         break
#
#     new_data = generate_noise()
#     print('generating image')
#     start = time.time()
#     # generated = model(data_i, mode='inference')
#     generated = model(new_data, mode='inference')
#     save_image(generated, f'results/rand_{i}.jpg')
#     print(type(generated))
#     end = time.time()
#     print('finished, took', end-start)
#
#     # img_path = data_i['path']
#     # for b in range(generated.shape[0]):
#     #     print('process image... %s' % img_path[b])
#     #     visuals = OrderedDict([('input_label', data_i['label'][b]),
#     #                            ('synthesized_image', generated[b])])
#     #     visualizer.save_images(webpage, visuals, img_path[b:b + 1])
#     #
#     # end = time.time()
#     # print('other shit took', end - start)
#
#
# webpage.save()
