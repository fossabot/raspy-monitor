from sqlite3.dbapi2 import connect
from flask import Flask, render_template, send_from_directory, redirect
from flask_socketio import SocketIO, emit
from os import environ, path
from flask_apscheduler import APScheduler
from modules.PiDB import PiDB
from modules.PiStats import PiStats


app = Flask(__name__, template_folder='html', static_folder='html')
socketio = SocketIO(app)
scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()


if 'DB_PATH' in environ:
    db_path = environ['DB_PATH']
else: 
    db_path = 'raspy_monitor.db'
pd = PiDB(db_path)
pd.initDb()


if 'ROOT_PATH' in environ:
    root_path = environ['ROOT_PATH']
else:
    root_path = "/"
ps = PiStats(root_path)


@app.route('/')
def index():
    return redirect('/home')


@app.route('/home')
def home():
    return render_template('home.html', debug='DEBUG' in environ)


@app.route('/<path:url>')
def lib(url):
    if path.exists('html/' + url):
        return send_from_directory('html', url)
    else:
        return send_from_directory('html', '404.html'), 404


@socketio.on('data')
def emitData(res):
    emit('data', {
        'system': ps.system(),
        'time': ps.time(),
        'memory': ps.memory(),
        'cpu': ps.cpu(),
        'netusage': ps.netUsage(),
        'diskusage': ps.diskUsage()
    })


@scheduler.task('cron', id='data_store_job', second='*/5')
def dataStoreJob():
    print('Test')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug='DEBUG' in environ)