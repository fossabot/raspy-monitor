const express = require('express');
const renderer = require('express-es6-template-engine');
const app = express();
const http = require('http');
const server = http.createServer(app);

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

server.listen(3000, () => {
  console.log('listening on *:3000');
});