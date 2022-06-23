#!/usr/bin/env python
#
# !!! Needs psutil installing:
#
#    $ sudo pip install psutil
#

import os
import sys
if os.name != 'posix':
    sys.exit('platform not supported')
from datetime import datetime

import psutil
from PIL import ImageFont
from cheap_oled import OLED_SSD1306, OLED_SH1106, OLED_Canvas

def bytes2human(n):
    """
    >>> bytes2human(10000)
    '9K'
    >>> bytes2human(100001221)
    '95M'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i+1)*10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = int(float(n) / prefix[s])
            return '%s%s' % (value, s)
    return "%sB" % n

def cpu_usage():
    # load average, uptime
    uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    av1, av2, av3 = os.getloadavg()
    return "Ld:%.1f %.1f %.1f Up: %s" \
            % (av1, av2, av3, str(uptime).split('.')[0])

def mem_usage():
    usage = psutil.virtual_memory()
    return "Mem: %s %.0f%%" \
            % (bytes2human(usage.used), 100 - usage.percent)


def disk_usage(dir):
    usage = psutil.disk_usage(dir)
    return "SD:  %s %.0f%%" \
            % (bytes2human(usage.used), usage.percent)

def network(iface):
    stat = psutil.net_io_counters(pernic=True)[iface]
    return "%s: Tx%s, Rx%s" % \
           (iface, bytes2human(stat.bytes_sent), bytes2human(stat.bytes_recv))

def stats(oled):
    font = ImageFont.load_default()
    font2 = ImageFont.truetype('fonts/C&C Red Alert [INET].ttf', 12)
    with OLED_Canvas(oled) as draw:
        draw.text((0, 0), cpu_usage(), font=font2, fill=255)
        draw.text((0, 14), mem_usage(), font=font2, fill=255)
        draw.text((0, 26), disk_usage('/'), font=font2, fill=255)
        draw.text((0, 38), network('eth0'), font=font2, fill=255)

def main(pi):
    oled = OLED_SSD1306(pi, port=1, address=0x3C)
    stats(oled)
    oled.close()

if __name__ == "__main__":
    import pigpio

    pi = pigpio.pi()

    if not pi.connected:
        exit()

    main(pi)

    pi.stop()
