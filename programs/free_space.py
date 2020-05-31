import uos

import vga2_bold_16x16 as font
import tftui

def main(ui):
    fs_stat = uos.statvfs('/')
    fs_size = fs_stat[0] * fs_stat[2]
    fs_free = fs_stat[0] * fs_stat[3]

    ui.cls()
    ui.center("System Size",0)
    ui.center("{:,}".format(fs_size), 1)

    ui.center("Free Space", 3)
    ui.center("{:,}".format(fs_free), 4)

    ui.center("Press to", 6)
    ui.wait("Continue", 7)

main(tftui.UI(font))

__import__("menu")      # return to turtleplotbot menu
