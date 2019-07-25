import numpy as np
from flask import Flask, render_template, Response, jsonify, request
from flask_socketio import SocketIO, send, emit
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!!'
CORS(app)
socketio = SocketIO(app)


def get_instance_vec(noise_vec):
    instance_vec = np.copy(noise_vec)
    for i, val in enumerate(np.unique(instance_vec)):
        instance_vec[instance_vec == val] = i

    return instance_vec


class StateManager:
    def __init__(self, dim=256):
        self.dim = dim
        self.col = 0
        self.fac = 16
        self.row = 8
        self.a, self.b = 32, 41
        self.label_map, self.instance_map = self.generate_noise()

    def generate_noise(self, dim=None):
        if dim is None:
            dim = self.dim
        # noise_vec = np.random.randint(50, 182, (dim, dim))
        # noise_vec = np.ones((dim, dim)) * 4
        # noise_vec[:self.row, :self.col] = 59

        # noise_vec = np.ones((dim, dim)) * 133
        noise_vec = np.ones((dim, dim)) * self.a
        middle = dim // 2
        low = middle - self.col
        high = middle + self.col
        noise_vec[low:high, low:high] = self.b
        # noise_vec[low:high, low:high] = 158

        instance_vec = get_instance_vec(noise_vec)

        # print(noise_vec)
        # noise_vec[:self.row] = noise_vec[:self.row] * 155
        # noise_vec[self.row:] = noise_vec[self.row:] * 169

        # noise_vec = np.random.randint(0, 182, (dim, dim))
        # self.row += 1
        fac = self.fac

        self.col += fac
        if low <= 0:
            # print(low, high, middle)
            self.a += 1
            if self.a > 187:
                self.a = 0
                self.b += 1
                if self.b > 187:
                    self.b = 0
            self.col = 0

        # self.col += fac
        # if self.col >= self.dim:
        #     self.col = 0
        #     self.row += fac
        #     if self.row > self.dim:
        #         self.row = fac
        return noise_vec, instance_vec

    def process_label_data(self, label_data=None):
        if not label_data or 'label_map' not in label_data:
            self.label_map, self.instance_map = self.generate_noise()
        else:
            # todo: convert to numpy array?
            self.label_map = label_data.get('label_map')
            self.instance_map = get_instance_vec(self.label_map)

    def get_state_dict(self):
        self.process_label_data()
        return dict(
            dim=self.dim,
            label_map=self.label_map.tolist(),
            instance_map=self.instance_map.tolist(),
            a=self.a,
            b=self.b,
        )


manager = StateManager()


@socketio.on('test-message')
def handle_test():
    print('AHHHHHHH real monsters'),


@socketio.on('new-label')
def update_label(label_data=None):
    # if not label_data:
    #     return

    global manager
    manager.process_label_data(label_data)


@app.route('/label')
def get_midi():
    global manager

    return jsonify(manager.get_state_dict())


if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0", port=42069)

