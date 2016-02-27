#!/usr/bin/env python2
# -*- coding: ascii -*-
"""
Simple Port Scanner (SPS) module. A tool to scan a host for open ports using trivial TCP connection initiation.
"""
from __future__ import print_function

"""
Copyright (c) 2011, Nikita Solovyev
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
may be used to endorse or promote products derived from this software without
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

import sys
import socket

def is_IP(str_in): 
    """
    Checks if provided argument `str_in` is a valid IPv4 adress.

    Args:
        str_in (string): String to check for validity.

    Returns:
        (bool): True if `str_in` is a valid IPv4 adress, False otherwise.
    """

    if not str_in:
        return False
    octets = str_in.split('.')
    if len(octets) != 4:
        return False
    for octet in octets:
        try:
            num = int(octet)
            if num<0 or num>255:
                return False
        except ValueError:
            return False
    return True

def is_hostname(str_in):
    """
    Checks if provided argument `str_in` is a valid hostname, i.e. could be
    resolved to IP.

    Args:
        str_in (string): String to check for validity.

    Returns:
        (bool): True if `str_in` could be resolved to IP, False otherwise.
    """

    try:
        addr = socket.gethostbyname(str_in)
        if not addr:
            return False
    except (ValueError, socket.error, socket.herror, socket.gaierror, socket.timeout):
        return False
    return True

def to_port_num(str_in):
    """
    Tries to coerce provided argument `str_in` to a port number integer
    value.

    Args:
        str_in (string): String to coerce to port number.

    Returns:
        (int) or (None): Integer port number if provided `str_in` is a valid
                         port number string, None otherwise.
    """

    try:
        port = int(str_in)
        if port<1 or port>65535:
            return None
    except ValueError:
        return None
    return port

def to_timeout(str_in):
    """
    Tries to coerce provided argument `str_in` to a valid timeout float
    value.

    Args:
        str_in (string): String to coerce to timeout.

    Returns:
        (float) or (None): Floating point number - timeout value if provided
                           `str_in` is a valid timeout string, None otherwise.
    """

    try:
        timeout = float(str_in)
        if timeout < 0:
            return None
    except ValueError:
        return None
    return timeout

def scan_host(host, first_port, last_port, timeout):
    """
    Scans `host` for open ports, starting from `first_port` up to `last_port`
    inclusive, waiting for connection establishment for `timeout` seconds.
    Prints to standard output.

    Args:
        host (string): host name or IP address to scan.
        first_port (int): First port in range to scan.
        last_port (int): Last port in range to scan.
        timeout (float): Time in seconds to wait for connection establishment.

    Returns:
        (None): Prints processing and resulting data to standard output.
    """

    opened_ports = []
    print('Starting scanner...')
    for port in xrange(first_port, last_port+1):
        print('Scanning port: %d' % port, end=' - ')
        address = (host, port)
        try:
            #Try to initialise a TCP connection
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            #Port is open if 'connect_ex' doesn't return error code                        
            if s.connect_ex(address) == 0:
                opened_ports.append(port)
                print('Open')
            else:
                print('Closed')
            s.close()
        except (ValueError, socket.error, socket.herror, socket.gaierror, socket.timeout):
            s.close()
            print('Error occured!')
            continue
    print('Scanning finished.')
    #Print summary
    if opened_ports:
        print('Opened ports on '+host+' are:')
        for port in opened_ports:
            try:
                service = '('+str(socket.getservbyport(port))+')'
            except (ValueError, socket.error, socket.herror, socket.gaierror, socket.timeout):
                service='(unknown)'
            print('%d ' % port, end='')
            print(service)
    else:
        print('No open ports found on '+host+' !')

def main():
    """
    Main control loop.

    Returns:
        (int): Return code, '0' - if execution was successful,
                            positive integer otherwise.
    """

    if len(sys.argv) > 1:
        #Run with command line arguments
        for arg in sys.argv:
            if arg in ('-h', '--help', '?'):
                print('Simple Port Scanner')
                print("""Usage: sps.py <host> [[[start_port] [end_port]] [conn_timeout]]

       host - IPv4 or host name to scan;
       start_port - first port in port range to scan, default is '1';
       end_port - last port in port range to scan, default is '65535';
       conn_timeout - time in seconds to wait for connection establishment,
                      floating point number, default is '0.1'.
                      """)
                print('Use -h, --help or ? to see this message')
                return 0
        if is_IP(sys.argv[1]) or is_hostname(sys.argv[1]):
            host = sys.argv[1]
            first_port = 1
            last_port = 65535
            timeout = 0.1
        else:
            print('First argument must be a valid hostname or IP address!')
            print('Use -h, --help or ? to see help on command line arguments')
            return 2
        if len(sys.argv) > 2:
            first_port = to_port_num(sys.argv[2])
            if not first_port:
                print('Second argument must be a valid port number - an integer between 1 and 65535!')
                print('Use -h, --help or ? to see help on command line arguments')
                return 2
            if len(sys.argv) > 3:
                last_port = to_port_num(sys.argv[3])
                if not last_port:
                    print('Third argument must be a valid port number - an integer between 1 and 65535!')
                    print('Use -h, --help or ? to see help on command line arguments')
                    return 2
                if len(sys.argv) > 4:
                    timeout = to_timeout(sys.argv[4])
                    if timeout is None:
                        print('Forth argument must be a valid timeout value in seconds - a positive floating point number!')
                        print('Use -h, --help or ? to see help on command line arguments')
                        return 2
                    elif timeout == 0:
                        timeout = 0.1
        #Perform scan
        scan_host(host, first_port, last_port, timeout)
        return 0
    else:
        #Run in interactive mode
        print('*******SimplePortScanner*******')
        print('*   Author: Nikita Solovyev   *')
        print('*   Version: 1.0              *')
        print('*******************************')
        print('Welcome to Simple Port Scanner!')
        while True:
            print('Type in the number corresponding to desired action:')
            print('0 - Exit')
            print('1 - Scan host')
            variant = raw_input("Enter your choice:")
            if variant == '0':
                return 0
            elif variant == '1':
                while True:
                    host = raw_input("Enter host for scanning:")
                    if not is_IP(host) and not is_hostname(host):
                        print('Host must be a valid hostname string or IP address!')
                        continue
                    break
                while True:
                    first_port = raw_input("Enter the first port in scanning range:")
                    first_port = to_port_num(first_port)
                    if not first_port:
                        print('Port number must be an integer between 1 and 65535!')
                        continue
                    break
                while True:
                    last_port = raw_input("Enter the last port in scanning range:")
                    last_port = to_port_num(last_port)
                    if not last_port:
                        print('Port number must be an integer between 1 and 65535!')
                        continue
                    break
                while True:
                    timeout = raw_input("Enter connection timeout in seconds(optional, enter 0 to use default value):")
                    timeout = to_timeout(timeout)
                    if timeout is None:
                        print('Timeout must be a positive floating point number or 0 for default value!')
                        continue
                    elif timeout == 0:
                        timeout = 0.1
                    break
                #Perform scan
                scan_host(host, first_port, last_port, timeout)
            else:
                print('Please enter the correct choice number!')
                continue

if __name__ == '__main__':
    err_code = main()
    exit(err_code)
