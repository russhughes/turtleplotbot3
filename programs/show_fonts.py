'''
scroll_fonts.py - Scroll Hershey fonts on display
'''

#pylint: disable-msg=import-error
import uos
import button
import vga2_bold_16x16 as font
import tftui

def main(ui):
    """
    Main routine
    """
    fonts = [font for font in uos.listdir('/fonts') if font.endswith('.fnt')]
    font_count = len(fonts)
    font_current = 0
    message="Hello!"
    again = True
    joystick = button.JoyStick()

    while again:
        ui.cls(fonts[font_current], 0)

        font = '/fonts/' + fonts[font_current]
        column = ui.width//2 - ui.size(message, scale=1, font=font)//2
        line = ui.height//2 - 16

        ui.draw(message, column, line, scale=1, font=font)

        ui.center('Up-Prev Dn-Next', 6)
        ui.center('other-exit', 7)
        btn = button.JoyStick().read()

        if btn == button.DOWN:
            font_current -= 1
            font_current %= font_count

        elif btn == button.UP:
            font_current += 1
            font_current %= font_count

        again = btn in [button.UP, button.DOWN]

main(tftui.UI(font))

__import__("menu")      # return to turtleplotbot menu
