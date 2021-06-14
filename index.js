const express = require('express');
const renderer = require('express-es6-template-engine');
const app = express();
const http = require('http');
const server = http.createServer(app);
const { Server } = require('socket.io');
const io = new Server(server);
const { readFile, readdir } = require('fs').promises;
const { promisify } = require('util');
const exec = promisify(require('child_process').exec)
const { type, arch, cpus, release, version, EOL } = require('os');
const txt_encoding = 'utf8';

class PiStats {
    constructor(root_path = ''){
        this.root_path = root_path;
    }

    async system(){
        const cpu_info = await readFile(`${this.root_path}/proc/cpuinfo`, txt_encoding);
        const os_release = await readFile(`${this.root_path}/etc/os-release`, txt_encoding);
        const hostname = await readFile(`${this.root_path}/proc/sys/kernel/hostname`, txt_encoding);
        let cpu_name = '';
        let model = '';
        let os_name = '';
        
        for(const line of cpu_info.split(EOL)){
            if(line.match(/^Hardware/)){
                cpu_name = line.replace('Hardware\t: ', '').replace(EOL, '');
            }
            else if(line.match(/^Model/)){
                model = line.replace('Model\t\t: ', '').replace(EOL, '');
            }
        }
        
        for(const line of os_release.split(EOL)){
            if(line.match(/^PRETTY_NAME/)){
                os_name = line.replace(/"/g, '').replace('PRETTY_NAME=', '').replace(EOL, '');
                break;
            }
        }

        return {
            model: model,
            processor: cpu_name,
            os_name: os_name,
            uname: {
                os: type(),
                arch: arch(),
                hostname: hostname,
                kernel_ver: release(),
                kernel_build: version()
            }
        }
    }

    async time(){
        const uptime = await readFile(`${this.root_path}/proc/uptime`, txt_encoding);
        const uptime_arr = uptime.split(' ')
        return {
            uptime: parseInt(uptime_arr[0])
        }
    }

    async cpu(){
        const cpu_num = cpus().length;
        const load_avg = await readFile(`${this.root_path}/proc/loadavg`, txt_encoding);
        const load_avg_arr = load_avg.split(' ');
        const temp = await readFile(`${this.root_path}/sys/devices/virtual/thermal/thermal_zone0/temp`, txt_encoding) / 1000;
        return {
            temp: temp / 1000,
            load: {
                last_minute: parseFloat((load_avg_arr[0] * 100 / cpu_num).toFixed(2)),
                last_five_minutes: parseFloat((load_avg_arr[1] * 100 / cpu_num).toFixed(2)),
                last_fifteen_minutes: parseFloat((load_avg_arr[2] * 100 / cpu_num).toFixed(2))
            }
        }
    }

    async diskUsage(){
        let disk_list = [];
        let used_total = 0;
        let total_total = 0;
        const mount_points = ['/', '/boot'];

        for(const mount of mount_points){
            const { stdout } = await exec(`df -k ${this.root_path}${mount}`);
            const data = stdout.split(EOL)[1].split(/\s+/g)
            const used = (data[2] / 1024).toFixed(2);
            const total = (data[1] / 1024).toFixed(2);
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

    async netUsage(){
        let net_list = [];
        let s_total = 0;
        let r_total = 0;

        const net_interfaces = await readdir(`${this.root_path}/sys/class/net`);
        const ignored_interfaces = ['lo'];

        for(const ifn of net_interfaces){
            if(! ignored_interfaces.includes(ifn)){
                const s_out = await readFile(`${this.root_path}/sys/class/net/${ifn}/statistics/tx_bytes`, txt_encoding);
                const s_bytes = (s_out.replace(EOL, '') / 1048576).toFixed(2);
                const r_out = await readFile(`${this.root_path}/sys/class/net/${ifn}/statistics/rx_bytes`, txt_encoding);
                const r_bytes = (r_out.replace(EOL, '') / 1048576).toFixed(2);
                s_total += s_bytes;
                r_total += r_bytes;
                net_list.push({
                    name: ifn,
                    sent: s_bytes,
                    received: r_bytes
                });
            }
        }

        return {
            interfaces: net_list,
            sent_total: s_total,
            received_total: r_total
        }
    }

    async memory(){
        const memory_out = await readFile(`${this.root_path}/proc/meminfo`, txt_encoding);
        const memory_out_arr = memory_out.split(EOL);
        let mem_total = 0;
        let mem_free = 0;
        let mem_buffers = 0;
        let mem_cached = 0;
        let swap_cached = 0;
        let swap_total = 0;
        let swap_free = 0;
        for(const info of memory_out_arr){
            const info_arr = info.split(/\s+/g);
            switch(info_arr[0]){
                case 'MemTotal:':   mem_total   = parseInt(info_arr[1]); break;
                case 'MemFree:':    mem_free    = parseInt(info_arr[1]); break;
                case 'Buffers:':    mem_buffers = parseInt(info_arr[1]); break;
                case 'Cached:':     mem_cached  = parseInt(info_arr[1]); break;
                case 'SwapCached:': swap_cached = parseInt(info_arr[1]); break;
                case 'SwapTotal:':  swap_total  = parseInt(info_arr[1]); break;
                case 'SwapFree':    swap_free   = parseInt(info_arr[1]); break;
                default: break;
            }
        }
        const mem_used = mem_total - (mem_free + mem_buffers + mem_cached);
        const swap_used = swap_total - (swap_free + swap_cached);
        return {
            memory: {
                total: (mem_total / 1024).toFixed(2),
                used: (mem_used / 1024).toFixed(2),
            },
            swap: {
                total: (swap_total / 1024).toFixed(2),
                used: (swap_used / 1024).toFixed(2)
            }
        }
    }
}

const ps = new PiStats('/')

const homeData = async () => {
    const diskusage = await ps.diskUsage();
    const time = await ps.time();
    const system = await ps.system();
    const cpu = await ps.cpu();
    const netusage = await ps.netUsage();
    const memory = await ps.memory();
    return {
        system: system,
        time: time,
        cpu: cpu,
        diskusage: diskusage,
        netusage: netusage,
        memory: memory
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
    });
    const home = setInterval(() => {
        homeData().then(data => {
            io.emit('home', data);
        });
    }, 1000);
    socket.on('disconnect', () => {        
        clearInterval(home);
    });
});

// Spawn server
server.listen(3000, () => {
    console.log('listening on *:3000');
});