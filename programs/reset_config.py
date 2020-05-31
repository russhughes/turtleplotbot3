
"""
Write ui.cfg with default values
"""

#pylint: disable-msg=import-error
import btree
import vga2_bold_16x16 as font
import button
import tftui

def reset_cfg():
    """
    Overwrite ui.cfg with default values
    """
    cfg_file = open("ui.cfg", "w+b")
    cfg_db = btree.open(cfg_file)

    # Add a default AP name and password
    cfg_db[b'AP_NAME'] = b'TurtleBot'
    cfg_db[b'AP_PASS'] = b'turtlebot'

    # Add any password for ap's you use
    cfg_db[b'MY_AP_NAME'] = b'mypassword'

    for key  in cfg_db:
        print("key", key, " = ", cfg_db[key])

    cfg_db.close()
    cfg_file.close()

def main(ui):
    """
    Ask for confirmation before reset
    """
    ui.cls("Reset", 2)
    ui.center("Config?", 3)
    ok = 0
    btn, ok = ui.select(0, 7, ("Reset", "Cancel"), ok)
    if btn == button.CENTER and ok == 0:
        reset_cfg()
        ui.cls("Resetting", 3)
        ui.center("Press to", 5)
        ui.wait("Continue", 6)
    else:
        ui.cls("Canceled", 3)
        ui.center("Press to", 5)
        ui.wait("Continue", 6)

main(tftui.UI(font))

__import__("menu")      # return to turtleplotbot menu
