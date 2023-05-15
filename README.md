![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

# Python Automation

Various Python automation scripts

## Table of Contents
- [Usage](#usage)
- [Showcase](#showcase)
- [Maintainers](#maintainers)

## Usage
- Clone the repo:
```sh
$ git clone https://github.com/tekore/Python
```

- Run the script
```sh
$ python3 ./<SCRIPT>
```

## Showcase
### Nagios-automation.py
Notable libraries used:
- Subprocess

Used to spawn SSH processes, redirect standard out to variables and redirect standard in to pseudo-terminals. 
- Pty

Used to spawn pseudo-terminals as to allow subprocess standard in to be written to.
- Threading

Used to spawn processes on seperate threads as deamons, limit the number of threads active at a time with 'Semaphore' and temporarily lock data sets to prevent race conditions with 'Lock'.
- Queue

Used to enable thread safe queueing of tasks.
### ssh.py
Cluster SSH created in python3
Notable libraries used:
- Subprocess
- Pty
- Threading
- Queue
- Improvments
Use the multiprocessing library alongside the threading library to take advantage of multicore systems

## Maintainers
[@Tekore](https://github.com/tekore)
