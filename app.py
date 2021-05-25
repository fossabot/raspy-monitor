from sqlite3.dbapi2 import connect
from flask import Flask, render_template, send_from_directory, redirect
from flask_socketio import SocketIO, emit
from os import environ, path
from flask_apscheduler import APScheduler
from modules.PiDB import PiDB
from modules.PiStats import PiStats


app = Flask(__name__, template_folder='public', static_folder='public')
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
pd.close()


if 'ROOT_PATH' in environ:
    root_path = environ['ROOT_PATH']
else:
    root_path = "/"
ps = PiStats(root_path)


@app.route('/')
def index():
    return redirect('/home')


@app.route('/<string:section>')
def home(section):
    return render_template('app.html', debug='DEBUG' in environ, section=section)


@app.route('/lib/<path:url>')
def lib(url):
    if path.exists('public/lib/' + url):
        return send_from_directory('public/lib', url)
    else:
        return send_from_directory('public/lib', '404.html'), 404


@socketio.on('home')
def emitData(res):
    emit('home', {
        'system': ps.system(),
        'time': ps.time(),
        'memory': ps.memory(),
        'cpu': ps.cpu(),
        'netusage': ps.netUsage(),
        'diskusage': ps.diskUsage()
    })

@socketio.on('statistics init')
def emitStatistics(res):
    pd = PiDB(db_path)
    emit('statistics init', {
        'data': pd.getLastDayStatistics()
    })


@socketio.on('statistics')
def emitStatistics(res):
    pd = PiDB(db_path)
    emit('statistics update', {
        'data': pd.getLastStatistics()
    })


@scheduler.task('cron', id='data_store_job', second='*/5')
def dataStoreJob():
    pd = PiDB(db_path)
    netusage_data = ps.netUsage()
    diskusage_data = ps.diskUsage()
    cpu_data = ps.cpu()
    memory_data = ps.memory()
    pd.insertIntoStatistics(
        memory=memory_data,
        cpu=cpu_data,
        disk=diskusage_data, 
        net=netusage_data
    )
    pd.close()


@scheduler.task('cron', id='del_old_job', hour=0, minute=0)
def delOldStore():
    pd = PiDB(db_path)
    pd.delOldStatistics()


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug='DEBUG' in environ, use_reloader=False)
