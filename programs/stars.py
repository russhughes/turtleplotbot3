'''
Draw a star from user provided values
'''
#pylint: disable-msg=import-error
from turtleplotbot import TurtlePlotBot
import vga2_bold_16x16 as font
import button
import tftui

def star(bot, points, length):
    '''
    Draw a 'n' pointed star with 'length' sides

    Args:
        sides: number of points
        length: length of each side
    '''
    angle = 180.0 - 180.0 / points
    bot.pendown()

    for _ in range(points):
        bot.forward(length)
        bot.left(angle)
        bot.forward(length)

    bot.penup()

def main(ui):
    """
    Main routine
    """
    points = 5
    length = 20
    ok = 0

    form = [
        [ui.HEAD, 0, "Draw A Star"],
        [ui.INT, 0, 2, "Points:", 8, 2, 2, points],
        [ui.INT, 0, 4, "Length:", 8, 4, 2, length],
        [ui.OK, 0, 7, ("Next", "Cancel"), ok],
    ]

    btn, ok = ui.form(form)
    if btn == button.CENTER and ok == 0:
        points = form[1][ui.VAL]
        length = form[2][ui.VAL]

        bot = TurtlePlotBot()
        star(bot, points, length)

main(tftui.UI(font))

__import__("menu")      # return to turtleplotbot menu
