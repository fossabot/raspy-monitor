import { promisify } from 'util';
import { type, arch, cpus, release, version, EOL, loadavg, hostname } from 'os';

const txt_encoding = 'utf8';
const { readFile, readdir } = require('fs').promises;
const exec = promisify(require('child_process').exec);

export class PiStats {
    root_path: string;
    mount_points: Array<string>;
    ignore_interfaces: Array<string>;

    constructor(root_path: string, mount_points: Array<string>, ignore_interfaces: Array<string>){
        this.root_path = root_path;
        this.mount_points = mount_points;
        this.ignore_interfaces = ignore_interfaces;
    }

    async system(): Promise<object>{
        const cpu_info = await readFile(`${this.root_path}/proc/cpuinfo`, txt_encoding);
        const os_release = await readFile(`${this.root_path}/etc/os-release`, txt_encoding);
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
                hostname: hostname(),
                kernel_ver: release(),
                kernel_build: version()
            }
        }
    }

    async time(): Promise<object>{
        const uptime = await readFile(`${this.root_path}/proc/uptime`, txt_encoding);
        const uptime_arr = uptime.split(' ')
        return {
            uptime: parseInt(uptime_arr[0])
        }
    }

    async cpu(): Promise<object>{
        const cpu_num = cpus().length;
        const load_avg_arr = loadavg();
        const temp = parseInt(await readFile(`${this.root_path}/sys/devices/virtual/thermal/thermal_zone0/temp`, txt_encoding)) / 1000;
        return {
            temp: temp,
            load: {
                last_minute: (load_avg_arr[0] * 100 / cpu_num).toFixed(2),
                last_five_minutes: (load_avg_arr[1] * 100 / cpu_num).toFixed(2),
                last_fifteen_minutes: (load_avg_arr[2] * 100 / cpu_num).toFixed(2)
            }
        }
    }

    async diskUsage(): Promise<object>{
        let disk_list = [];
        let used_total: number = 0;
        let total_total: number = 0;

        for(const mount of this.mount_points){
            const { stdout } = await exec(`df -k ${this.root_path}${mount}`);
            const data = stdout.split(EOL)[1].split(/\s+/g)
            const used = (parseInt(data[2]) / 1024).toFixed(2);
            const total = (parseInt(data[1]) / 1024).toFixed(2);
            used_total += parseInt(used);
            total_total += parseInt(total);
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

    async netUsage(): Promise<object>{
        let net_list = [];
        let s_total = 0;
        let r_total = 0;

        const net_interfaces = await readdir(`${this.root_path}/sys/class/net`);

        for(const ifn of net_interfaces){
            if(! this.ignore_interfaces.includes(ifn)){
                const s_out = await readFile(`${this.root_path}/sys/class/net/${ifn}/statistics/tx_bytes`, txt_encoding);
                const s_bytes = (parseInt(s_out.replace(EOL, '')) / 1048576).toFixed(2);
                const r_out = await readFile(`${this.root_path}/sys/class/net/${ifn}/statistics/rx_bytes`, txt_encoding);
                const r_bytes = (parseInt(r_out.replace(EOL, '')) / 1048576).toFixed(2);
                s_total += parseInt(s_bytes);
                r_total += parseInt(r_bytes);
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

    async memory(): Promise<object>{
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