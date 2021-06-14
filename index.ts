import express from 'express';
import { Server } from 'socket.io';
import { PiStats } from './lib/pistats';

const http = require('http');
const renderer = require('express-es6-template-engine');
const app = express();
const server = http.createServer(app);
const io = new Server(server);
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
app.get('/', (req: any, res: any) => {
    res.redirect('/home');
});
app.get('/:section', (req: any, res: any) => {
    res.render('app', {locals: {section: req.params.section}});
});

// SocketIO
io.on('connection', (socket: any) => {
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