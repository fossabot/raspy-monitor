from flask import Flask, render_template, send_from_directory, redirect
from flask_socketio import SocketIO, emit
from os import environ, path
import modules.PiStats as p


app = Flask(__name__, template_folder='html', static_folder='html')
socketio = SocketIO(app)


@app.route('/')
def index():
    return redirect('/home')


@socketio.on('data')
def helloSocket(res):
    emit('data', {
        'system': p.system(),
        'time': p.time(),
        'memory': p.memory(),
        'cpu': p.cpu(),
        'netusage': p.netUsage(),
        'diskusage': p.diskUsage()
    })


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/<path:url>')
def lib(url):
    if path.exists('html/' + url):
        return send_from_directory('html', url)
    else:
        return send_from_directory('html', '404.html'), 404


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug='DEBUG' in environ)