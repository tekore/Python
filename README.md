![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

# Python Automation

Various Python automation scripts

## Table of Contents
- [Install](#install)
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

Used to spawn SSH processes, redirect standard output to variables and redirect standard in to a pseudo-terminals. 
- Pty

Used to spawn pseudo-terminals as to allow the subprocess standard in to be written to.
- Threading

Used to spawn processes on seperate threads as deamons, limit the number of threads active at a time with 'Semaphore' and temporarily lock data sets to prevent Race Conditions with 'Lock'.
- Queue

Used to enable queueing of tasks in a thread safe manner.

## Maintainers
[@Tekore](https://github.com/tekore)
