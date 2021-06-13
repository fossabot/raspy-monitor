const express = require('express');
const renderer = require('express-es6-template-engine');
const app = express();
const http = require('http');
const server = http.createServer(app);
const { Server } = require("socket.io");
const io = new Server(server);
const fs = require('fs')
const os = require('os');
const promisify = require('util').promisify;
const exec = promisify(require('child_process').exec)

class PiStats {
    constructor(root_path = ''){
        this.root_path = root_path;
    }

    system(){
        const cpu_info = fs.readFileSync(`${this.root_path}/proc/cpuinfo`, 'utf8').split('\n');
        const os_release = fs.readFileSync(`${this.root_path}/etc/os-release`, 'utf8').split('\n');
        let cpu_name = '';
        let model = '';
        let os_name = '';

        for(const line of cpu_info){
            if(line.match(/^Hardware/)){
                cpu_name = line.replace('Hardware\t: ', '').replace('\n', '');
            }
            else if(line.match(/^Model/)){
                model = line.replace('Model\t\t: ', '').replace('\n', '');
            }
        }
        
        for(const line of os_release){
            if(line.match(/^PRETTY_NAME/)){
                os_name = line.replace(/"/g, '').replace('PRETTY_NAME=', '').replace('\n', '');
                break;
            }
        }

        return {
            model: model,
            processor: cpu_name,
            os_name: os_name,
            uname: {
                os: os.type(),
                arch: os.arch(),
                hostname: os.hostname(),
                kernel_ver: os.release(),
                kernel_build: os.version()
            }
        }
    }

    time(){
        const uptime = parseInt(fs.readFileSync(`${this.root_path}/proc/uptime`, 'utf8').split(' ')[0]);
        return {
            uptime: uptime
        }
    }

    cpu(){
        const cpu_num = os.cpus().length;
        const load_avg = fs.readFileSync(`${this.root_path}/proc/loadavg`, 'utf8').split(' ');
        const temp = fs.readFileSync(`${this.root_path}/sys/devices/virtual/thermal/thermal_zone0/temp`, 'utf8') / 1000;
        return {
            temp: temp,
            load: {
                last_minute: parseFloat((load_avg[0] * 100 / cpu_num).toFixed(2)),
                last_five_minutes: parseFloat((load_avg[1] * 100 / cpu_num).toFixed(2)),
                last_fifteen_minutes: parseFloat((load_avg[2] * 100 / cpu_num).toFixed(2))
            }
        }
    }

    async diskusage(){
        let disk_list = [];
        let used_total = 0;
        let total_total = 0;
        const mount_points = ['/', '/boot'];

        for(const mount of mount_points){
            const { stdout } = await exec(`df -k ${this.root_path}${mount}`);
            const data = stdout.split('\n')[1].split(/\s+/g)
            const used = parseInt(data[2] / 1024);
            const total = parseInt(data[1] / 1024);
            used_total += used;
            total_total += total;
            disk_list.push({
                mount_point: mount,
                used: used,
                total: total
            });
        }
        
        return {
            paths: disk_list,
            used_total: used_total,
            total_total: total_total
        }
    }
}

const ps = new PiStats('/')

const homeData = async () => {
    const diskusage = await ps.diskusage();
    const time = ps.time();
    const system = ps.system();
    const cpu = ps.cpu();
    return {
        system: system,
        time: time,
        cpu: cpu,
        diskusage: diskusage
    }
}

// Express settings
app.engine('html', renderer);
app.set('view engine', 'html');
app.set('views', './views');

// Routings
app.use('/static', express.static('static'));
app.get('/', (req, res) => {
    res.redirect('/home');
});
app.get('/:section', (req, res) => {
    res.render('app', {locals: {section: req.params.section}});
});

// SocketIO
io.on('connection', (socket) => {
    homeData().then(data => {
            io.emit('home', data);
        }
    );
    const home = setInterval(() => {
        homeData().then(data => {
                io.emit('home', data);
            }
        );
    }, 1000);
    socket.on('disconnect', () => {        
        clearInterval(home);
    });
});

// Spawn server
server.listen(3000, () => {
    console.log('listening on *:3000');
});