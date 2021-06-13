Vue.component('cpu', {
    props: ['percentage'],
    template: `<div class="cpu-bar-fill" v-bind:percentage="percentage" v-bind:style="'width: ' + percentage + '%'"></div>`
});

Vue.component('disk', {
    props: ['used', 'total', 'path'],
    template: `<div class="disk-bar-fill" v-bind:used="used" v-bind:total="total" v-bind:style="'width: ' + ( 100 * used / total ) + '%'"></div>`
});

Vue.component('uptime', {
    props: ['type', 'value'],
    template: `<span class="uptime-card" v-bind:label="type">{{ value }}</span>`
});

Vue.component('memory', {
    props: ['used', 'total'],
    template: `<div class="disk-bar-fill" v-bind:used="used" v-bind:total="total" v-bind:style="'width: ' + ( 100 * used / total ) + '%'"></div>`
})

const vm = new Vue({
    el: '.container',    
    data: {
        dataLoaded: false,
        section: '',
        api: {
            cpu: {
                load: {
                    last_minute: 0,
                    last_five_minutes: 0,
                    last_fifteen_minutes: 0
                }
            },
            system: {
                uname: {}
            },
            diskusage:{
                paths: []
            },
            memory: {
                memory: {},
                swap: {}
            },
            netusage: {
                interfaces: []
            }
        },
        uptime: {
            days: 0,
            hours: 0,
            minutes: 0,
            seconds: 0
        }
    },
    methods: {
        changeNav: function(e){
            this.section = e.target.id.replace('-button', '');
        },
        dataUpdate: function(res){
            console.log(res);
            if(! this.dataLoaded){
                this.api.system = res.system;
                this.api.time = res.time;
                this.uptime.days = Math.floor(res.time.uptime / 86400);
                res.time.uptime -= this.uptime.days * 86400;
                this.uptime.hours = Math.floor(res.time.uptime / 3600);
                res.time.uptime -= this.uptime.hours * 3600;
                this.uptime.minutes = Math.floor(res.time.uptime / 60);
                this.uptime.seconds = res.time.uptime - this.uptime.minutes * 60
                this.dataLoaded = true;
            }
            //this.api.memory = res.memory;
            this.api.cpu = res.cpu;
            //this.api.netusage = res.netusage;
            this.api.diskusage = res.diskusage;            
        },
        uptimeUpdate: function(){
            this.uptime.seconds += (this.uptime.seconds != 59) || -59;
            this.uptime.minutes += (this.uptime.seconds == 0) + ((this.uptime.minutes == 59 && this.uptime.seconds == 0) * -60 )
            this.uptime.hours += (this.uptime.minutes == 0 && this.uptime.seconds == 0) + ((this.uptime.hours == 23 && this.uptime.minutes == 0) * -24 )
            this.uptime.days += (this.uptime.hours == 0 && this.uptime.minutes == 0 && this.uptime.seconds == 0)
        },
        backgroundJob: function(){
            this.socket.emit(this.section, '');
        }
    },
    created: function(){
        this.socket = io();
        this.socket.on('home', this.dataUpdate);
        this.backgroundJob();
        this.uptimeJobInterval = setInterval(this.uptimeUpdate, 1000);
        this.backgroundJobInterval = setInterval(this.backgroundJob, 5000);
    },
    destroyed: function(){
        clearInterval(this.backgroundJobInterval);
        clearInterval(this.uptimeJobInterval);
    }
});