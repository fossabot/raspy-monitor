# RasPy-Monitor
[![Build Master](https://github.com/lemniskett/raspy-monitor/actions/workflows/build-master.yml/badge.svg)](https://github.com/lemniskett/raspy-monitor/actions/workflows/build-master.yml)

A monitoring tool for Raspberry Pi written with Express, currently it's not yet done as not everything is implemented and things are constantly changing and breaking, here's a list of TODOs:

1. Display statistics from the last 24 hours.
2. Monitor system services.
3. Non-environment-variable configuration.
4. Monitor multiple Raspberry Pi devices.
5. (Maybe) Performance tweaking.

## Usage
### With npm
You'll need atleast Node.JS 14 runtime :

```sh
npm install
npm run build
env NODE_ENV=production node build/index.js
```

App can be accessed from port 3000

## Configuration
Configuration currently only can be done with environment variables :
| Variable | Description |
| --- | --- |
| IGNORE_INTERFACES | Exclude network interface from network monitoring, defaults to `lo` (loopback interface). |
| MOUNT_POINTS | Specify mount points to be monitored, defaults to `/`. |
| ROOT_PATH | Specify which operating system root to be monitored, useful for running inside containers. |
| DB_PATH | Specify where to create or look for sqlite database, defaults to `./raspy_monitor.db` (`/config/raspy_monitor.db` for docker container). |
| DEBUG | For development purposes, setting it to anything will enable debugging, both backend and frontend. |

## Screenshots

![Screenshot 1](imgs/screenshot-1.png)

![Screenshot 2](imgs/screenshot-2.png)
