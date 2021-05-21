from os import uname, listdir, environ
from datetime import datetime
from re import search
from psutil import virtual_memory, swap_memory, boot_time, getloadavg, disk_usage, cpu_count
from sys import stderr


if 'ROOT_PATH' in environ:
    root_path = environ['ROOT_PATH']
else:
    root_path = "/"


def system():
    try:
        cpu_info_file = open(root_path + 'proc/cpuinfo')
        cpu_info_lines = cpu_info_file.readlines()
        cpu_info_file.close()

        for line in cpu_info_lines:
            if search('Hardware', line):
                cpu_name = line.replace('Hardware\t: ', '').replace('\n', '')
            elif search('Model', line):
                model = line.replace('Model\t\t: ', '').replace('\n', '')
        os_release_file = open(root_path + 'etc/os-release')
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
        print('Error when trying to access resources, is the $ROOT_PATH correct?', file=stderr)
        print(str(e))


def time():
    date = datetime.now()
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
        'uptime': int(date.timestamp() - boot_time())
    }


def memory():
    memory = virtual_memory()
    swap = swap_memory()
    return {
        'memory': {
            'total': int(memory.total / 1048576),
            'used': int(memory.used / 1048576)
        },
        'swap': {
            'total': int(swap.total / 1048576),
            'used': int(swap.used / 1048576)
        }
    }


def cpu():
    try:
        cpu_num = cpu_count()
        load_avg = getloadavg()
        temp_file = open(root_path + 'sys/devices/virtual/thermal/thermal_zone0/temp')
        temp = int(int(temp_file.read()) / 1000)
        temp_file.close()
        return {
            'temp': temp,
            'load': {
                'last_minute': round(load_avg[0] * 100 / cpu_num, 2),
                'last_five_minutes': round(load_avg[1] * 100 / cpu_num, 2),
                'last_fifteen_minutes': round(load_avg[2] * 100 / cpu_num, 2)
            }
        }
    except FileNotFoundError as e:
        print('Error when trying to access resources, is the $ROOT_PATH correct?', file=stderr)
        print(str(e))


def netUsage():
    try:
        net_list = []
        sent_total = 0
        received_total = 0
        net_interfaces = listdir(root_path + 'sys/class/net')
        if 'IGNORE_INTERFACES' in environ:
            ignored_interfaces = environ['IGNORE_INTERFACES'].split()
        else:
            ignored_interfaces = ['lo']
        for i in net_interfaces:
            if i not in ignored_interfaces:
                s_file = open(root_path + 'sys/class/net/' + i + '/statistics/tx_bytes')
                r_file = open(root_path + 'sys/class/net/' + i + '/statistics/rx_bytes')
                s_bytes = int(int(s_file.read().replace('\n', '')) / 1048576)
                r_bytes = int(int(r_file.read().replace('\n', '')) / 1048576)
                s_file.close()
                r_file.close()
                sent_total += s_bytes
                received_total += r_bytes
                net_list.append({'name': i, 'sent': s_bytes, 'received': r_bytes})
        return {'interfaces': net_list, 'sent_total': sent_total, 'received_total': received_total}
    except FileNotFoundError as e:
        print('Error when trying to access resources, is the $ROOT_PATH correct?', file=stderr)
        print(str(e))


def diskUsage():
    disk_list = []
    used_total = 0
    total_total = 0
    if 'MOUNT_POINTS' in environ:
        mount_points = environ['MOUNT_POINTS'].split()
    else:
        mount_points = ['/']
    for i in mount_points:
        data = disk_usage(root_path + i)
        used = int(data.used / 1048576)
        total = int(data.total / 1048576)
        used_total += used
        total_total += total
        disk_list.append({'mount_point': i, 'used': used, 'total': total})
    return {'paths': disk_list, 'used_total': used_total, 'total_total': total_total}