const express = require('express');
const renderer = require('express-es6-template-engine');
const app = express();
const http = require('http');
const server = http.createServer(app);
const { Server } = require("socket.io");
const io = new Server(server);
const fs = require('fs')
const os = require('os');

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
}

const ps = new PiStats('/')

const homeData = () => {
    return {
        system: ps.system()
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
    const home = setInterval(() => {
        io.emit('home', homeData())
    }, 1000);
    socket.on('disconnect', () => {        
        clearInterval(home);
    });
});

// Spawn server
server.listen(3000, () => {
    console.log('listening on *:3000');
});