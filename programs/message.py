'''
Write text using user provided values
'''
#pylint: disable-msg=import-error
import uos
from turtleplotbot import TurtlePlotBot
import vga2_bold_16x16 as font
import tftui
import button

def main(ui):
    """
    Write text using user provided values
    """
    fonts = [f for f in uos.listdir("/fonts") if f.endswith(".fnt")]
    fonts_len = len(fonts)
    message = "Hello!"
    scale = 0
    ok = 0

    form = [
        [ui.HEAD, 0, "Write A Message"],
        [ui.STR, 0, 2, "Message:", 0, 3, 16, message],
        [ui.SEL, 0, 5, "Scale:", 6, 5, ("1", "2", "3"), scale],
        [ui.OK, 0, 7, ("Next", "Cancel"), ok],
    ]

    again = True
    while again:
        btn, ok = ui.form(form)
        if btn == button.CENTER and ok == 0:
            message = form[1][ui.VAL]
            scale = form[2][ui.VAL]+1
            font = 0
            font = ui.menu("Choose A Font", fonts, font)
            if font is not None:

                while again:
                    ui.cls(fonts[font], 0)
                    font_file = "/fonts/" + fonts[font]
                    width = ui.size(message, font=font_file, scale=scale)

                    ui.draw(
                        message,
                        ui.width//2 - width//2,
                        ui.height//2,
                        ui.fg,
                        font=font_file,
                        scale=scale)

                    response = 0
                    btn, response = ui.select(0, 7, ("Draw", "Back", "Quit"), response)
                    if btn == button.CENTER:
                        if response == 0:
                            ui.cls(0)
                            bot = TurtlePlotBot()
                            bot.setscale(scale)
                            bot.write(message, "/fonts/" + fonts[font])
                            bot.done()
                            again = False
                        elif response == 2:
                            again = False

                    if btn == button.UP:
                        font -= 1
                        font %= fonts_len

                    elif btn == button.DOWN:
                        font += 1
                        font %= fonts_len

        else:
            again = False

main(tftui.UI(font))

__import__("menu")      # return to turtleplotbot menu
