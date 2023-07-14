#!/usr/bin/env python3

#    Small hackish script to convert an U-Boot memdump to a binary image
#
#    Copyright (C) 2015  Simon Baatz
#    Updated: 2023 John Feehley
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from argparse import ArgumentParser
from re import compile
from os import devnull
from sys import stdout, stderr, __stdout__, __stderr__
from tqdm import tqdm
from binwalk import scan


class Utility():
    def __init__(self):
        self.args = self.get_args()
        return 


    def get_args(self):
        parser = ArgumentParser()
        parser.add_argument(
            "logfile"
        )
        parser.add_argument(
            "-l",
            "--line_length",
            help    = "Bytes in each line",
            default = 0x10
        )
        parser.add_argument(
            "-o",
            "--outfile",
            help    = "File to store the results",
            default = "output.bin"
        )
        return vars(parser.parse_args())




class MDB_Converter():
    def __init__(self, **kwargs):
        self.logfile = kwargs["logfile"]
        self.outfile = kwargs["outfile"]

        self.bytes_in_line   = kwargs["bytes_in_line"]
        self.pattern         = compile("^[0-9a-fA-F]{8}\:")
        self.logfile_content = []
        self.binary_data     = [] 


    def disable_output(self):
        stdout = open(devnull, "w")
        stderr = open(devnull, "w")
        return 


    def enable_output(self):
        stdout = __stdout__
        stderr = __stderr__
        return 


    def read_log(self):
        with open(self.logfile, 'r') as fptr:
            self.logfile_content = fptr.readlines()
        return


    def write_image(self):
        with open(self.outfile, 'wb') as fptr:
            fptr.write(self.binary_data)


    def extract_image(self): 
        print("[+] Extracting...")
        self.disable_output()
        scan(
            self.outfile, 
            signature = True, 
            quiet = True, 
            extract = True
        )
        print("\033[H\033[J", end="")
        self.enable_output()
        return 

    def convert_log(self):
        c_addr     = None
        hex_to_chr = {}
        line_count = 0

        for line in self.logfile_content:
            line_count += 1
            if "md 0x" in line or "md.b 0x" in line:
                line_count += 1
                self.logfile_content = self.logfile_content[line_count:-1]
                break

        print("[+] Repairing image...")
        for line in tqdm(self.logfile_content):
            line = line[:-1]
            try:
                data, ascii_data = line.split("    ", maxsplit = 1)
            except ValueError:
                #print("\033[H\033[J", end="")
                print("[!] Rerun after stripping more of the logfile")
                print("\tsometimes there are additional lines above and below")
                exit(-1)

            straddr, strdata = data.split(maxsplit = 1)
            addr = int.from_bytes(
                bytes.fromhex(straddr[:-1]), 
                byteorder = "big"
            )
            if c_addr != addr - self.bytes_in_line:
                if c_addr:
                    exit(f"[!] Unexpected c_addr in line: '{line}'")
            c_addr = addr
            data = bytes.fromhex(strdata)
            if len(data) != self.bytes_in_line:
                exit(f"[!] Unexpected number of bytes in line: '{line}'")

            for b,c in zip(data, ascii_data):
                try: 
                    if hex_to_chr[b] != c: 
                        exit("[!] Inconsistency between hex data and " +\
                             "ASCII data in line (or the lines before): " +\
                            f"'{line}'")
                except KeyError:
                    hex_to_chr[b] = c

            self.binary_data.append(data)
        self.binary_data = b''.join(self.binary_data)
        return


def main():
    #args = Utility.get_args()
    utilities = Utility()
    
    mdb_converter = MDB_Converter(
        logfile = utilities.args["logfile"],
        outfile = utilities.args["outfile"],
        bytes_in_line = utilities.args["line_length"]
    )

    mdb_converter.read_log()
    mdb_converter.convert_log()
    mdb_converter.write_image()
    mdb_converter.extract_image()
    return

if __name__ == '__main__':
    exit(main())
