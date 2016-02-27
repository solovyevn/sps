Simple Port Scanner
===================

Simple Port Scanner (SPS) is a tool to scan a host for open ports using trivial TCP connection initiation. For every port in specified range SPS tries to initiate connection via TCP, if connection is established, then the port is considered open, otherwise closed.


sps.py
======

New version of SPS, remake of original using 'asyncio' and 'argparse'. Supports IPv4 and IPv6.


Requirements
------------

- Python 3.4


Installation & Usage
--------------------

No installation step is required, just copy 'sps.py' to your machine, set as executable, and run it. If the shebang line is not recognised run as 'python3 sps.py'.

Simple Port Scanner can be run both from command line with arguments, see below, or in interactive mode if no command line arguments provided.

Usage: sps.py [-h] [-s START_PORT] [-e END_PORT] [-t TIMEOUT] [-b BATCH]
              [-i INTERVAL] [--version] [-v | -q]
              host

positional arguments:
  host                  IP or host name to scan

optional arguments:
  -h, --help            show this help message and exit
  -s START_PORT, --start_port START_PORT
                        first port in port range to scan (default: 1)
  -e END_PORT, --end_port END_PORT
                        last port in port range to scan (default: 65535)
  -t TIMEOUT, --timeout TIMEOUT
                        time in seconds to wait for connection establishment,
                        floating point number (default: 0.1)
  -b BATCH, --batch BATCH
                        maximum size of a batch of concurrent port scans
                        (default: 10)
  -i INTERVAL, --interval INTERVAL
                        time interval in seconds between successive batches of
                        concurrent port scans, floating point number (default:
                        1.0)
  --version             show program's version number and exit
  -v, --verbose         display additional output during execution
  -q, --quiet           display only the result

Note: Ports are scanned asynchronously in batches of specified size. Setting batch size to big numbers (>1000) is not recommended, as it may lead to insufficient number of available file descriptors, depending on your machine setup. Also, depending on host that will be scanned, attempting many connections per second may lead to your host being blocked, so use batch size and interval settings with care.


sps_2011.py
===========

Old, original version of SPS. Supports only IPv4.


Requirements
------------

- Python 2.7


Installation & Usage
--------------------

No installation step is required, just copy 'sps.py' to your machine, set as executable, and run it. If the shebang line is not recognised run as 'python3 sps.py'.

Simple Port Scanner can be run both from command line with arguments, see below, or in interactive mode if no command line arguments provided.

Usage: sps_2011.py <host> [[[start_port] [end_port]] [conn_timeout]]
       host - IPv4 or host name to scan;
       start_port - first port in port range to scan, default is '1';
       end_port - last port in port range to scan, default is '65535';
       conn_timeout - time in seconds to wait for connection establishment,
                      floating point number, default is '0.1'.


LICENSE
=======

Copyright (c) 2011, Nikita Solovyev
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
