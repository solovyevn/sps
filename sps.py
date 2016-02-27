#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Port Scanner (SPS) is a tool to scan a host for open ports using trivial TCP connection initiation.
"""

"""
Copyright (c) 2015, Nikita Solovyev
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
import argparse
import socket
import asyncio
from timeit import default_timer as timer
from math import ceil

#Defaults for user provided arguments
DEFAULT_TIMEOUT = 0.1
DEFAULT_INTERVAL = 1.0
DEFAULT_BATCH_SIZE = 10
DEFAULT_VERBOSITY = 1

def to_addrinfo(host_str):
    """
    Tries to create a TCP socket 'addrinfo' without specific port for a host 
    provided in `host_str`. Sets 'cannonname' in 'addrinfo' to `host_str` if
    it's resolved successfully.

    Args:
        host_str (string): Name or IPv4, or IPv6 of a host.

    Returns:
        tuple: A tuple of 'addrinfo' without port in a form (family, type, 
               proto, cannonname, sockaddr).

    Raises:
        ValueError: If `host_str` is an invalid IP address, or host name, that 
                    can't be resolved.
    """

    if not host_str:
        raise ValueError("argument must not be None, host name or IP address must be provided")
    try:
        addrinfo_lst = socket.getaddrinfo(host_str, None, type=socket.SOCK_STREAM)
        if not addrinfo_lst[0][3]:
            addrinfo_lst[0] = addrinfo_lst[0][:3] + (host_str, ) + addrinfo_lst[0][4:]
    except socket.gaierror as e:
        raise ValueError("argument must be a valid IPv4/IPv6 address or host name, that could be resolved") from e
    return addrinfo_lst[0]

def to_port(port_str):
    """
    Tries to convert `port_str` string to an integer port number.

    Args:
        port_str (string): String representing integer port number in range 
                       from 1 to 65535.

    Returns:
        int: Integer port number.

    Raises:
        ValueError: If `port_str` could not be converted to integer in range 
                    from 1 to 65535.
    """

    try:
        port_int = int(port_str)
    except ValueError:
        raise ValueError("argument must represent an integer number")
    if port_int<1 or port_int>65535:
        raise ValueError("argument must be an integer in range from 1 to 65535")
    return port_int

def to_time_sec(time_str):
    """
    Tries to convert `time_str` to a valid time non negative floating point number.

    Args:
        time_str (string): String representing non negative float - time 
                           in seconds.

    Returns:
        float: Time as non negative floating point number.

    Raises:
        ValueError: If `time_str` could not be converted to float or is less 
                    than 0.
    """

    try:
        time_float = float(time_str)
    except ValueError:
        raise ValueError("argument must represent a floating point number")
    if time_float < 0:
        raise ValueError("argument must be a non-negative floating point number")
    return time_float

def to_positive_int(int_str):
    """
    Tries to convert `int_str` string to a positive integer number.

    Args:
        int_str (string): String representing a positive integer number.

    Returns:
        int: Positive integer number.

    Raises:
        ValueError: If `int_str` could not be converted to a positive integer.
    """

    try:
        int_int = int(int_str)
    except ValueError:
        raise ValueError("argument must represent an integer number")
    if int_int<1:
        raise ValueError("argument must be a positive integer number")
    return int_int

def ap_typeerror_dec(conv_func):
    """
    Decorator for conversion functions, wraps `conv_func` to raise
    'argparse.ArgumentTypeError' instead of 'ValueError' keeping its error
    message.

    Args:
        conv_func (callable): Conversion function or any callable, that tries 
                              to convert its argument, and if it's not possible
                              raises 'ValueError.

    Returns:
        callable: Decorated `conv_func`, that raises 
                  'argparse.ArgumentTypeError' instead of 'ValueError'.

    Raises:
        argparse.ArgumentTypeError: If `conv_func` raises 'ValueError'.
    """
    def wrapper(*args, **kwargs):
        try:
            return conv_func(*args, **kwargs)
        except ValueError as e:
            raise argparse.ArgumentTypeError(str(e)) from e
    return wrapper

@asyncio.coroutine
def scan_port(addrinfo, timeout=0.1, verbosity=0):
    """
    Coroutine. Ties to connect to a host and port provided in `addrinfo` 
    to determine if the port is open, waiting for connection establishment 
    for `timeout` seconds.
    Prints to standard output if `verbosity` is not 0.

    Args:
        addrinfo (tuple): 5-tuple of (family, type, proto, cannonname, sockaddr)
                          from 'to_addrinfo()' or 'socket.getaddrinfo()'.
        timeout (Optional[float]): Time in seconds to wait for connection 
                                   establishment. Defaults to 0.1.
        verbosity (Otional[int]): Integer verbosity level:
                                0 (quiet) no display;
                                1 currently not in use;
                                2 (verbose) display detailed execution 
                                             information;
                                Defaults to 0.

    Returns:
        bool: True if connection is established and the port is therefore open, 
              False otherwise.
    """

    start_time = timer()
    #Coroutine result
    is_open = False
    if verbosity > 1:
        print("Scanning port {}...".format(addrinfo[-1][1]))
    s = socket.socket(*addrinfo[:3])
    #asyncio requires the socket to be non-blocking, 
    #so setting socket timeout to 0.0
    s.setblocking(False)
    try:
        #Try to connect to the port asynchronously in coroutine.
        #Since socket timeout has to be 0.0, use 'wait_for' coroutine 
        #to wait for timeout
        loop = asyncio.get_event_loop() 
        yield from asyncio.wait_for(loop.sock_connect(s, addrinfo[-1]), 
                                    timeout=timeout)
        #If got this far, then connection is successful
        is_open = True
        info = " ({})".format(s)
    except (OSError, asyncio.TimeoutError) as e:
        #Connection attempt failed
        is_open = False
        info = ''
        if str(e):
            info = " ({})".format(e)
    finally:
        s.close()
    end_time = timer()
    if verbosity > 1:
        print("Finished scanning port {} in {:.4F}s - {}{}".format(
            addrinfo[-1][1], end_time-start_time, 
            "OPEN" if is_open else "CLOSED", info))
    return is_open

def scan(addrinfo, first_port, last_port, timeout=0.1, batch=10, interval=1.0, 
         verbosity=1):
    """
    Performs the scan of a host provided in `addrinfo` for open ports, starting 
    from `first_port` up to `last_port` inclusive, waiting for connection 
    establishment for `timeout` seconds. Port range is separated in batches of 
    a maximum of `batch` size, and each batch is scanned concurrently with a 
    time interval between batches set by `interval` in seconds.
    Prints to standard output if `verbosity` is not 0.

    Args:
        addrinfo (tuple): 5-tuple of (family, type, proto, cannonname, sockaddr)
                          from 'to_addrinfo()' or 'socket.getaddrinfo()'.
        first_port (int): First port in range to scan.
        last_port (int): Last port in range to scan.
        timeout (Optional[float]): Time in seconds to wait for connection 
                                   establishment. Defaults to 0.1.
        batch (Optional[int]): Number of ports to scan concurrently as a batch.
                               Defaults to 10.
        interval (Optional[float]): Time in seconds to wait between batches of
                                    ports to scan. Defaults to 1.0.
        verbosity (Otional[int]): Integer verbosity level:
                                0 (quiet) no display;
                                1 (normal) display execution information;
                                2 (extended) display detailed execution 
                                             information;
                                Defaults to 1.

    Returns:
        list: List of open ports.

    Raises:
        RuntimeError: If any unhandled exceptions occur during ports' scan. The 
                      returned instance of Runtime error has custom attributes:
                      `open_ports`: list of any ports that were found to be 
                                    open;
                      `errors`: dictionary mapping occurred exceptions' 
                                instances to port numbers, scans of which lead 
                                to exceptions.
    """

    if verbosity > 0:
        print("Starting scan of {} ({}) [{}-{}]...".format(addrinfo[3], 
                                        addrinfo[-1][0], first_port, last_port))
    start_time = timer()
    try:
        main_loop = asyncio.get_event_loop()
        #Dictioanry mapping port number to resulting 'Future'
        results = {}
        #Full port range to scan
        ports = range(first_port, last_port+1)
        #Split full range in batches
        batch_count = ceil(len(ports)/batch)
        for i in range(batch_count):
            #Working with each batch
            batch_start_time = timer()
            #Get ports in this batch from full range
            batch_ports = ports[i*batch:i*batch+batch]
            if verbosity > 0:
                print("Scanning batch {}/{}, ports {}-{}...".format(i+1, 
                                batch_count, batch_ports[0], batch_ports[-1]))
            #Create Tasks for batch's ports, modifying addrinfo 
            #to put in concrete port
            tasks = [main_loop.create_task(scan_port(
                addrinfo[:-1]+((addrinfo[-1][0], port) + addrinfo[-1][2:],), 
                timeout, verbosity)) for port in batch_ports]
            #Extend resulting dict with this batch's ports and 
            #corresponding 'Futures'
            results.update(dict(zip(batch_ports, tasks)))
            #Perform scan of current batch
            main_loop.run_until_complete(asyncio.wait(tasks))
            #Wait for specified interval before next batch. 
            #Required in cases when there're connection limits on the host
            main_loop.run_until_complete(asyncio.sleep(interval))
            batch_end_time = timer()
            if verbosity > 0:
                print("Batch {}/{} scan finished in {:.4F}s.".format(i+1, 
                               batch_count, batch_end_time-batch_start_time))
        end_time = timer()
        if verbosity > 0:
            print("Scan of {} ({}) [{}-{}] finished in {:.4F}s".format(
                         addrinfo[3], addrinfo[-1][0], first_port, last_port, 
                         end_time-start_time))
    except KeyboardInterrupt:
        if verbosity > 0:
            print("\nScan interrupted by user after {:.4F}s".format(
                                                           timer()-start_time))
    finally:
        main_loop.close()
    #Parse results
    open_ports = []
    errors = {}
    for port in results:
        try:
            #Ports with 'True' result are open
            if results[port].result():
                open_ports.append(port)
        except Exception as e:
            #Create custom dictionary, mapping occurred exceptions to 
            #port number keys
            errors[port] = e
    #Raise exception with custom attributes if any exception occurred
    if errors:
        runtime_error = RuntimeError("Exceptions occurred during port scan.")
        runtime_error.open_ports = open_ports
        runtime_error.errors = errors
        raise runtime_error
    return open_ports

def _scan(addrinfo, first_port, last_port, timeout=0.1, batch=10, interval=1.0, 
          verbosity=1):
    """
    Wrapper for 'scan' to print results and/or exceptions and return 
    error code for the script.
    Prints to standard output.

    Args:
        addrinfo (tuple): 5-tuple of (family, type, proto, cannonname, sockaddr)
                          from 'to_addrinfo()' or 'socket.getaddrinfo()'.
        first_port (int): First port in range to scan.
        last_port (int): Last port in range to scan.
        timeout (Optional[float]): Time in seconds to wait for connection 
                                   establishment. Defaults to 0.1.
        batch (Optional[int]): Number of ports to scan concurrently as a batch.
                               Defaults to 10.
        interval (Optional[float]): Time in seconds to wait between batches of
                                    ports to scan. Defaults to 1.0.
        verbosity (Otional[int]): Integer verbosity level:
                                0 (quiet) display only the result or errors;
                                1 (normal) display execution information;
                                2 (extended) display detailed execution 
                                             information;
                                Defaults to 1.

    Returns:
        int: Error code, '0' - if 'scan' hasn't raised any exceptions, 
                         otherwise '1'.
    """

    #Return code
    err_code = 0
    try:
        open_ports = scan(addrinfo, first_port, last_port, timeout, batch, 
                          interval, verbosity)
    except RuntimeError as e:
        #Display any errors
        print(e)
        if verbosity > 0 and e.errors:
            for err_port in e.errors: 
                print("Port {}: {}".format(err_port, e.errors[err_port]))
        open_ports = e.open_ports
        err_code = 1
    #Print summary
    if open_ports:
        print("Open ports on {} ({}) in range [{}-{}]:".format(
                        addrinfo[3], addrinfo[-1][0], first_port, last_port))
        for port in open_ports:
            try:
                service = socket.getservbyport(port)
            except OSError:
                service = "unknown"
            print("{} ({})".format(port, service))
    else:
        print("No open ports found on {} ({}) in range [{}-{}].".format(
                        addrinfo[3], addrinfo[-1][0], first_port, last_port))
    return err_code

def main():
    """
    Main control loop.

    Returns:
        int: Return code, '0' - if execution was successful,
             positive integer otherwise.
    """

    #CLI arguments defenitions
    parser = argparse.ArgumentParser(description="Scans 'host' for open ports in range from 'start_port' to 'end_port' inclusive using TCP connection initialisation, waiting for 'timeout' seconds for connection establishment.")
    parser.add_argument(metavar="host", dest='addrinfo', 
                        help="IP or host name to scan", 
                        type=ap_typeerror_dec(to_addrinfo))
    parser.add_argument("-s", "--start_port", 
                        help="first port in port range to scan (default: 1)", 
                        type=ap_typeerror_dec(to_port), default=1)
    parser.add_argument("-e", "--end_port", 
                        help="last port in port range to scan (default: 65535)", 
                        type=ap_typeerror_dec(to_port), default=65535)
    parser.add_argument("-t", "--timeout", 
                        help="time in seconds to wait for connection establishment, floating point number (default: {})".format(
                        DEFAULT_TIMEOUT), type=ap_typeerror_dec(to_time_sec), 
                        default=DEFAULT_TIMEOUT)
    parser.add_argument("-b", "--batch",
                        help="maximum size of a batch of concurrent port scans (default: {})".format(
                        DEFAULT_BATCH_SIZE), 
                        type=ap_typeerror_dec(to_positive_int), default=DEFAULT_BATCH_SIZE)
    parser.add_argument("-i", "--interval",
                        help="time interval in seconds between successive batches of concurrent port scans, floating point number (default: {})".format(
                        DEFAULT_INTERVAL), type=ap_typeerror_dec(to_time_sec), 
                        default=DEFAULT_INTERVAL)
    parser.add_argument("--version", action="version", 
                        version="%(prog)s 2.0, Copyright (c) 2015 Nikita Solovyev")
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument("-v", "--verbose", dest='verbosity',
                                 help="display additional output during execution", 
                                 action="store_const", const=2, default=DEFAULT_VERBOSITY)
    verbosity_group.add_argument("-q", "--quiet", dest='verbosity',
                                 help="display only the result", 
                                 action="store_const", const=0, default=DEFAULT_VERBOSITY)
    if len(sys.argv) > 1:
        #Run with command line arguments
        args = parser.parse_args()
        #Perform scan
        return _scan(args.addrinfo, args.start_port, args.end_port, 
                     args.timeout, args.batch, args.interval, args.verbosity)
    else:
        #Run in interactive mode
        print('*******SimplePortScanner*******')
        print('*   Author: Nikita Solovyev   *')
        print('*   Version: 2.0              *')
        print('*******************************')
        print('Welcome to Simple Port Scanner!')
        while 1:
            print('Type in the number corresponding to desired action:')
            print('0 - Exit')
            print('1 - Scan host')
            variant = input("Enter your choice:")
            if variant == '0':
                return 0
            elif variant == '1':
                try:
                    while 1:
                        host = input("Enter host name or IP for scanning:")
                        try:
                            addrinfo = to_addrinfo(host)
                        except ValueError as e:
                            print("Invalid host value:", e)
                            continue
                        break
                    while 1:
                        first_port = input("Enter the first port in scanning range (default: 1):")
                        if first_port == '':
                            first_port = 1
                        else:
                            try:
                                first_port = to_port(first_port)
                            except ValueError as e:
                                print("Invalid first port value:", e)
                                continue
                        break
                    while 1:
                        last_port = input("Enter the last port in scanning range (default: 65535):")
                        if last_port == '':
                            last_port = 65535
                        else:
                            try:
                                last_port = to_port(last_port)
                            except ValueError as e:
                                print("Invalid last port value:", e)
                                continue
                        break
                    while 1:
                        timeout = input("Enter the connection timeout to use in seconds (default: {}):".format(DEFAULT_TIMEOUT))
                        if timeout == '':
                            timeout = DEFAULT_TIMEOUT
                        else:
                            try:
                                timeout = to_time_sec(timeout)
                            except ValueError as e:
                                print("Invalid timeout value:", e)
                                continue
                        break
                    while 1:
                        verbosity = input("Display detailed information during execution?[(Y)es/(N)o] (default: No):")
                        if verbosity.lower() in ('y', 'yes'):
                            verbosity = 2
                        elif verbosity.lower() in ('', 'n', 'no'):
                            verbosity = DEFAULT_VERBOSITY
                        else:
                            print("Please enter (Y)es or (N)o, or press [Enter] for default.")
                            continue
                        break
                    while 1:
                        batch = input("Enter the maximum size of a batch of concurrent port scans (default: {}):".format(DEFAULT_BATCH_SIZE))
                        if batch == '':
                            batch = DEFAULT_BATCH_SIZE
                        else:
                            try:
                                batch = to_positive_int(batch)
                            except ValueError as e:
                                print("Invalid batch value:", e)
                                continue
                        break
                    while 1:
                        interval = input("Enter the time interval in seconds between successive batches of concurrent port scans (default: {}):".format(DEFAULT_INTERVAL))
                        if interval == '':
                            interval = DEFAULT_INTERVAL
                        else:
                            try:
                                interval = to_time_sec(interval)
                            except ValueError as e:
                                print("Invalid interval value:", e)
                                continue
                        break
                except KeyboardInterrupt:
                    print('\n')
                    continue
                #Perform scan
                _scan(addrinfo, first_port, last_port, timeout, batch, interval, verbosity)
            else:
                print("Please enter the correct choice number.")
                continue

if __name__ == '__main__':
    err_code = main()
    exit(err_code)
