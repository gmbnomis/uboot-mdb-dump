# uboot-mdb-dump

This is a small script hacked together to convert a memory dump
obtained by `md.b` in U-Boot via a serial console to binary form. (The
particular U-Boot used here was an ancient U-Boot 2008.10)

The script expects the output of `md.b` on stdin and outputs the
binary data to stdout. It does a couple of consistency checks when
doing so (consecutive addresses at the beginning of lines; mapping
between hex representation and ASCII representation of a byte is
consistent.)

## Example usage

- In U-Boot, do e.g. the following (and capture the serial communication):

    ```
    => md.b 0x4000000 0x50
    04000000: de ad be ef de ad be ef de ad be ef de ad be ef    ................
    04000010: de ad be ef de ad be ef de ad be ef de ad be ef    ................
    04000020: de ad be ef de ad be ef de ad be ef de ad be ef    ................
    04000030: de ad be ef de ad be ef de ad be ef de ad be ef    ................
    04000040: de ad be ef de ad be ef de ad be ef de ad be ef    ................
    => 
    ```

    Note: The length must be a multiple of 0x10!

- Remove all but the output of `md.b` from the serial capture file.

- Pipe it through uboot_mdb_to_image.py

    ```
    # python3 uboot_mdb_to_image.py < test.cap | hexdump -C
    00000000  de ad be ef de ad be ef  de ad be ef de ad be ef  |................|
    *
    00000050
    ```
