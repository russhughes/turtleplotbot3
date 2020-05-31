"""
menu_example.py - Show a menu of numbers that the user can select and show the
number picked. Pressing the left button will exit the menu and program.
"""

import vga2_bold_16x16 as font
import tftui

def main(ui):
    """
    Main routine
    """

    menu = [
        "One",
        "Two",
        "Three",
        "Four",
        "Five",
        "Six",
        "Seven",
        "Eight",
        "Nine"
    ]

    option = 0
    while option is not None:
        option = ui.menu("Pick a Number", menu, option)
        if option:
            ui.cls("You Picked:", 2)
            ui.center(menu[option], 3)
            ui.center("Press to", 5)
            ui.wait("Continue", 6)

    ui.cls("Bye!")

main(tftui.UI(font,1))

__import__("menu")      # return to turtleplotbot menu

