"""
hello.py: Simple example using write
"""
#pylint: disable-msg=import-error
from turtleplotbot import TurtlePlotBot
import vga2_bold_16x16 as font
import tftui

def main(ui):
    """
    Write "Hello!"
    """
    message = "Hello!"
    ui.cls()
    width = ui.size(message, scale=2, font="fonts/scripts.fnt")
    column = ui.width//2 - width//2
    line = ui.height//2 - 16
    ui.draw(message, column, line, scale=2, font="fonts/scripts.fnt")

    bot = TurtlePlotBot()
    bot.setscale(2)
    bot.write(message, "fonts/scripts.fnt")
    bot.done()

main(tftui.UI(font))

__import__("menu")      # return to turtleplotbot menu
