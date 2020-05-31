'''
Write a message.
'''

from turtleplotbot import TurtlePlotBot
bot=TurtlePlotBot()

# make the text 2 times larger then the default
bot.setscale(2)
bot.write("Hello!", "fonts/scripts.fnt")
bot.done()

__import__("menu")      # return to turtleplotbot menu
