# Copyright (c) Nordic Semiconductor ASA
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form, except as embedded into a Nordic
#    Semiconductor ASA integrated circuit in a product or a software update for
#    such product, must reproduce the above copyright notice, this list of
#    conditions and the following disclaimer in the documentation and/or other
#    materials provided with the distribution.
#
# 3. Neither the name of Nordic Semiconductor ASA nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
# 4. This software, with or without modification, must only be used with a
#    Nordic Semiconductor ASA integrated circuit.
#
# 5. Any software provided in binary form under this license must not be reverse
#    engineered, decompiled, modified and/or disassembled.
#
# THIS SOFTWARE IS PROVIDED BY NORDIC SEMICONDUCTOR ASA "AS IS" AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY, NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NORDIC SEMICONDUCTOR ASA OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import os
import logging
from sys import platform

if platform == 'linux':
    import psutil

from . import Exceptions

# Lock file management.
# ref: https://refspecs.linuxfoundation.org/FHS_3.0/fhs/ch05s09.html
#
# Stored in /var/lock:
# The naming convention which must be used is "LCK.." followed by the base name of the device.
# For example, to lock /dev/ttyS0 the file "LCK..ttyS0" would be created.
# HDB UUCP lock file format:
# process identifier (PID) as a ten byte ASCII decimal number, with a trailing newline

def lockpid(lockfile):
    if (os.path.isfile(lockfile)):
        with open(lockfile) as fd:
            lockpid = fd.read()

        try:
            return int(lockpid)
        except:
            logging.info("Lockfile is invalid. Overriding it..")
            os.remove(lockfile)
            return 0

    return 0

def lock(port):
    if platform != 'linux':
        return

    tty = os.path.basename(port)
    lockfile = f'/var/lock/LCK..{tty}'

    lockedpid = lockpid(lockfile)
    if lockedpid:
        if lockedpid == os.getpid():
            return

        if psutil.pid_exists(lockedpid):
            raise Exceptions.LockedException(f"Device {port} is locked")
        else:
            logging.info("Lockfile is stale. Overriding it..")
            os.remove(lockfile)

    fd = open(lockfile, 'w')
    with open(lockfile, 'w') as fd:
        fd.write(f'{os.getpid():10}')

def unlock(port):
    if platform != 'linux':
        return

    tty = os.path.basename(port)
    lockfile = f'/var/lock/LCK..{tty}'

    lockedpid = lockpid(lockfile)
    if lockedpid == os.getpid():
        os.remove(lockfile)
