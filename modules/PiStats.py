from os import uname, listdir, environ, cpu_count, statvfs
from datetime import datetime
from re import search, sub
from sys import stderr


class PiStats:
    def __init__(self, root_path):
        self.root_path = root_path


    def system(self):
        try:
            cpu_info_file = open(self.root_path + 'proc/cpuinfo')
            cpu_info_lines = cpu_info_file.readlines()
            cpu_info_file.close()

            for line in cpu_info_lines:
                if search('Hardware', line):
                    cpu_name = line.replace('Hardware\t: ', '').replace('\n', '')
                elif search('Model', line):
                    model = line.replace('Model\t\t: ', '').replace('\n', '')
            os_release_file = open(self.root_path + 'etc/os-release')
            for line in os_release_file.readlines():
                if search('PRETTY_NAME', line):
                    os_name = line.replace('"', '').replace('PRETTY_NAME=', '').replace('\n', '')
                    break
            uname_data = uname()
            return {
                'model' : model,
                'processor': cpu_name,
                'os_name': os_name,
                'uname': {
                    'os': uname_data.sysname,
                    'arch': uname_data.machine,
                    'hostname': uname_data.nodename,
                    'kernel_ver': uname_data.release,
                    'kernel_build': uname_data.version
                }
            }
        except NameError as e:
            print("Some data can't be parsed, currently only supports parsing data from Raspberry Pi.", file=stderr)
            print(str(e))
        except FileNotFoundError as e:
            print('Error when trying to access resources, is the ROOT_PATH correct?', file=stderr)
            print(str(e))


    def time(self):
        try:
            date = datetime.now()
            uptime_file = open(self.root_path + 'proc/uptime')
            uptime = int(float(uptime_file.read().split()[0]))
            uptime_file.close()
            return {
                'date': {
                    'year': date.year,
                    'month': date.month,
                    'weekday': date.isoweekday(),
                    'day': date.day,
                    'hour': date.hour,
                    'minute': date.minute,
                    'second': date.second
                },
                'uptime': uptime
            }
        except FileNotFoundError as e:
            print('Error when trying to access resources, is the ROOT_PATH correct?', file=stderr)
            print(str(e))


    def memory(self):
        try:
            mem_info_file = open(self.root_path + 'proc/meminfo')
            mem_info_lines = mem_info_file.readlines()
            mem_info_file.close()
            for line in mem_info_lines:
                if search('^MemTotal:', line):
                    mem_total = int(sub('[a-zA-Z\ :\\n]', '', line))
                elif search('^MemFree:', line):
                    mem_free = int(sub('[a-zA-Z\ :\\n]', '', line))
                elif search('^Buffers:', line):
                    mem_buffers = int(sub('[a-zA-Z\ :\\n]', '', line))
                elif search('^Cached:', line):
                    mem_cached = int(sub('[a-zA-Z\ :\\n]', '', line))
                elif search('^SwapCached:', line):
                    swap_cached = int(sub('[a-zA-Z\ :\\n]', '', line))
                elif search('^SwapTotal:', line):
                    swap_total = int(sub('[a-zA-Z\ :\\n]', '', line))
                elif search('^SwapFree:', line):
                    swap_free = int(sub('[a-zA-Z\ :\\n]', '', line))
                    break
            mem_used = mem_total - (mem_free + mem_buffers + mem_cached)
            swap_used = swap_total - (swap_free + swap_cached)
            return {
                'memory': {
                    'total': int(mem_total / 1024),
                    'used': int(mem_used / 1024)
                },
                'swap': {
                    'total': int(swap_total / 1024),
                    'used': int(swap_used / 1024)
                }
            }
        except FileNotFoundError as e:
            print('Error when trying to access resources, is the ROOT_PATH correct?', file=stderr)
            print(str(e))

    def cpu(self):
        try:
            cpu_num = cpu_count()
            loadavg_file = open(self.root_path + 'proc/loadavg')
            loadavg = loadavg_file.read().split()
            loadavg_file.close()
            temp_file = open(self.root_path + 'sys/devices/virtual/thermal/thermal_zone0/temp')
            temp = int(int(temp_file.read()) / 1000)
            temp_file.close()
            return {
                'temp': temp,
                'load': {
                    'last_minute': round(float(loadavg[0]) * 100 / cpu_num, 2),
                    'last_five_minutes': round(float(loadavg[1]) * 100 / cpu_num, 2),
                    'last_fifteen_minutes': round(float(loadavg[2]) * 100 / cpu_num, 2)
                }
            }
        except FileNotFoundError as e:
            print('Error when trying to access resources, is the ROOT_PATH correct?', file=stderr)
            print(str(e))


    def netUsage(self):
        try:
            net_list = []
            s_total = 0
            r_total = 0

            net_interfaces = listdir(self.root_path + 'sys/class/net')
            if 'IGNORE_INTERFACES' in environ:
                ignored_interfaces = environ['IGNORE_INTERFACES'].split()
            else:
                ignored_interfaces = ['lo']
            for i in net_interfaces:
                if i not in ignored_interfaces:
                    s_file = open(self.root_path + 'sys/class/net/' + i + '/statistics/tx_bytes')
                    r_file = open(self.root_path + 'sys/class/net/' + i + '/statistics/rx_bytes')
                    s_bytes = int(int(s_file.read().replace('\n', '')) / 1048576)
                    r_bytes = int(int(r_file.read().replace('\n', '')) / 1048576)
                    s_file.close()
                    r_file.close()
                    s_total += s_bytes
                    r_total += r_bytes
                    net_list.append({'name': i, 'sent': s_bytes, 'received': r_bytes})
            return {'interfaces': net_list, 'sent_total': s_total, 'received_total': r_total}
        except FileNotFoundError as e:
            print('Error when trying to access resources, is the ROOT_PATH correct?', file=stderr)
            print(str(e))


    def diskUsage(self):
        disk_list = []
        used_total = 0
        total_total = 0
        if 'MOUNT_POINTS' in environ:
            mount_points = environ['MOUNT_POINTS'].split()
        else:
            mount_points = ['/']
        for i in mount_points:
            data = statvfs(self.root_path + i)
            total_raw = data.f_blocks * data.f_frsize
            available_raw = data.f_bavail * data.f_frsize
            used_raw = total_raw - available_raw
            total = int(total_raw / 1048576)
            used = int(used_raw / 1048576)
            used_total += used
            total_total += total
            disk_list.append({'mount_point': i, 'used': used, 'total': total})
        return {'paths': disk_list, 'used_total': used_total, 'total_total': total_total}