"""
menu.py Drawbot Menu System

MIT License
Copyright (c) 2020 Russ Hughes

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
#pylint: disable-msg=import-error
import time
import sys
import gc
import network
import uos

import vga2_bold_16x16 as font
import tftui
import button

def reload(mod):
    """
    reload: Removes a module and re-imports allowing you to re-run programs

    Args:
        mod (str): Name of module to reload
    """
    mod_name = mod.__name__
    del sys.modules[mod_name]
    gc.collect()
    return __import__(mod_name)

def connect_ap(uio):
    """
    scan for ap's and allow user to select and connect to it
    """
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    if sta_if.isconnected():
        sta_if.disconnect()

    ap_name = ""
    ap_pass = ""

    uio.cls("Scanning", 3)

    scan = sta_if.scan()
    connect = 0

    connect = uio.menu("Select AP", scan, connect, 0)
    if connect is not None:
        ap_name = scan[connect][0]
        ap_pass = uio.get(ap_name)
        ok = 0
        form = [
            [uio.HEAD, 0, "Select AP"],
            [uio.CENTER, 1, "Connect to"],
            [uio.CENTER, 2, ap_name],
            [uio.STR, 0, 4, "Password:", 0, 5, 16, ap_pass],
            [uio.OK, 0, 7, ("Continue", "Cancel"), ok],
        ]

        btn, ok = uio.form(form)
        if btn == button.CENTER and ok == 0:
            ap_pass = form[3][uio.VAL]

            uio.cls("Connecting", 1)
            uio.center("to", 2)
            uio.center(ap_name, 3)
            sta_if.connect(ap_name, ap_pass)
            timeouts = 30
            while not sta_if.isconnected() and timeouts:
                uio.center(str(timeouts), 7)
                timeouts -= 1
                time.sleep(1)

            uio.cls("Connection", 0)
            if sta_if.isconnected():
                uio.put(ap_name, ap_pass)
                uio.center("Successful", 1)
                ifconfig = sta_if.ifconfig()
                uio.center("IP Address:", 3)
                uio.center(ifconfig[0], 4)
            else:
                uio.center("Failed", 1)
                sta_if.active(False)

            uio.center("Press to", 6)
            uio.wait("Continue", 7)

def disconnect_ap(uio):
    """
    disconnect from ap
    """
    sta_if = network.WLAN(network.STA_IF)
    uio.cls()
    uio.center("Disable AP", 0, uio.fg_hdr, uio.bg_hdr)
    uio.center("Disconnecting", 3)
    sta_if.active(False)
    uio.center("Press to", 6)
    uio.wait("Continue", 7)

def enable_ap(uio):
    """
    Ask user for ap_name and ap_password then start ap and save
    ap_name and ap_pass to uio.cfg btree file
    """
    ap_name = uio.get(b'AP_NAME')
    ap_pass = uio.get(b'AP_PASS')
    ok = 0

    form = [
        [uio.HEAD, 0, "Enable AP"],
        [uio.STR, 0, 1, "AP Name:", 0, 2, 16, ap_name],
        [uio.STR, 0, 4, "Password:", 0, 5, 16, ap_pass],
        [uio.OK, 0, 7, ("Continue", "Cancel"), ok],
    ]

    again = True
    while again:
        btn, ok = uio.form(form)
        if btn == button.CENTER and ok == 0:
            ap_name = form[1][uio.VAL]
            ap_pass = form[2][uio.VAL]

            if not 1 <= len(ap_pass) <= 7:
                sta_ap = network.WLAN(network.AP_IF)
                if sta_ap.active():
                    sta_ap.active(False)
                sta_ap.active(True)
                if len(ap_pass) == 0:
                    sta_ap.config(essid=ap_name, authmode=network.AUTH_OPEN)
                    uio.put(b'AP_NAME', ap_name)
                    uio.put(b'AP_PASS', ap_pass)
                else:
                    sta_ap.config(
                        essid=ap_name,
                        password=ap_pass,
                        authmode=network.AUTH_WPA_WPA2_PSK)
                    uio.put(b'AP_NAME', ap_name)
                    uio.put(b'AP_PASS', ap_pass)

                uio.cls()
                uio.center("Access Point", 0)
                if sta_ap.active():
                    uio.put(ap_name, ap_pass)
                    uio.center("Enabled", 1)
                    ifconfig = sta_ap.ifconfig()
                    uio.center("IP Address:", 3)
                    uio.center(ifconfig[0], 4)
                    again = False
                else:
                    uio.center("Failed", 2)
                    sta_ap.active(False)
            else:
                    uio.center("Password must", 1)
                    uio.center("be at least 8", 2)
                    uio.center("characters or", 3)
                    uio.center("be blank", 4)

            uio.center("Press to", 6)
            uio.wait("Continue", 7)
        else:
            again = False

def disable_ap(uio):
    """
    disable AP if running
    """
    sta_ap = network.WLAN(network.AP_IF)
    uio.cls()
    uio.center("Disable AP", 0, uio.fg_hdr, uio.bg_hdr)
    uio.center("Disabling AP", 3)
    sta_ap.active(False)
    uio.center("Press to", 6)
    uio.wait("Continue", 7)

def run_program(uio):
    """
    show list of python programs and allow user to select one to run
    """
    programs = uos.listdir("/programs")
    program = 0
    program = uio.menu("Run Program", programs, program)
    if program is not None:
        mod_name = "".join(programs[program].split(".")[:-1])
        if mod_name in sys.modules:
            reload(sys.modules[mod_name])
        else:
            __import__(mod_name)

def main_menu(uio):
    """
    show user main menu and call method based on selection
    """
    menu = [
        ("Connect to AP", connect_ap),
        ("Disconnect AP", disconnect_ap),
        ("Enable AP", enable_ap),
        ("Disable AP", disable_ap),
        ("Run Program", run_program),
        ("Quit", None)]

    option = 0
    while True:
        option = uio.menu("DrawBot Menu", menu, option, 0)
        if option not in [None, 5]:
            if callable(menu[option][1]):
                menu[option][1](uio)
        else:
            uio.cls("Exiting", 1)
            uio.center("to", 2)
            uio.center("REPL", 3)
            uio.center("Press to", 5)
            uio.wait("Continue", 6)
            uio.cls()
            break

main_menu(tftui.UI(font))
sys.exit()
