"""
ui.py - UI for LCD and 5 way button
"""

# pylint: disable-msg=import-error
from machine import Pin, SPI
import st7789
import button
import btree

# pylint: disable-msg=invalid-name
const = lambda x: x

ALNUM = [
    ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM", "\x1b \x7f"],
    ["qwertyuiop", "asdfghjkl", "zxcvbnm", "\x1b \x7f"],
    ["!@#$%^&*()", "1234567890", "<>+-_=\?", "\x1b \x7f"],
    ["+,-./:;", "<=>?@[\]", "^_`{|}~", "\x1b \x7f"]
]

NUM = [
    ["123", "456", "789", ".\x1b\x7f"]
]

# pylint: disable-msg=too-many-instance-attributes
class UI:
    """
    ui: MicroPython LCD user interface class using JoyStick

    Args:
        font (bitmap font): Bitmap font to use in UI

        Returns:
            UI object
    """
    def __init__(self, font, log=0):
        # init i2c tft
        self.back_light = Pin(4, Pin.OUT)
        self.back_light.value(1)

        self.display = st7789.ST7789(
            SPI(
                2,
                baudrate=30000000,
                polarity=1,
                phase=1,
                sck=Pin(18),
                mosi=Pin(19)),
            135,
            240,
            reset=Pin(23, Pin.OUT),
            cs=Pin(5, Pin.OUT),
            dc=Pin(16, Pin.OUT),
            rotation=3)

        self.display.init()
        self.font = font
        self.width = self.display.width()
        self.height = self.display.height()
        self.max_chars = self.width // self.font.WIDTH
        self.max_lines = self.height // self.font.HEIGHT
        self.fg = st7789.WHITE
        self.bg = st7789.BLUE
        self.fg_act = st7789.RED
        self.bg_act = st7789.WHITE
        self.fg_hdr = st7789.WHITE
        self.bg_hdr = st7789.RED
        self.joystick = button.JoyStick()

    @staticmethod
    def get(cfg_name):
        """
        get: get config setting from btree ui.cfg file if one exists

        Args:
            cfg_name ([str, bytes]): name of setting to load

        Returns:
            (string): value of setting
        """
        name = cfg_name.encode() if isinstance(cfg_name, str) else cfg_name
        try:
            cfg_file = open("ui.cfg", "r+b")
        except OSError:
            cfg_file = open("ui.cfg", "w+b")

        cfg_db = btree.open(cfg_file)
        try:
            cfg_value = cfg_db[name]
        except KeyError:
            cfg_value = b''

        cfg_db.close()
        cfg_file.close()

        return cfg_value.decode('ascii')

    @staticmethod
    def put(cfg_name, cfg_value):
        """
        put: put config setting into btree ui.cfg file

        Args:
            cfg_name ([str, bytes, bytearray]): name of setting to store
            cfg_value ([str, bytes, bytearray]): value of setting to store
        """
        if isinstance(cfg_name, str):
            name = cfg_name.encode()
        else:
            name = cfg_name

        if isinstance(cfg_value, str):
            value = cfg_value.encode()
        else:
            value = cfg_value

        try:
            cfg_file = open("ui.cfg", "r+b")
        except OSError:
            cfg_file = open("ui.cfg", "w+b")

        cfg_db = btree.open(cfg_file)
        cfg_db[name] = value
        cfg_db.close()
        cfg_file.close()

    def size(
            self,
            message,
            font="/fonts/romant.fnt",
            scale=1):
        '''
        Returns the width of a message if drawn in the specified font and scale.

        Args:
            message (str): The message to write
            font_file (str): The Hershy font file to use, defaults to romant.fnt
            scale (int): Scaling factor
        '''
        width = 0
        with open(font, "rb", buffering=0) as file:
            characters = int.from_bytes(file.read(2), 'little')
            if characters > 96:
                begins = 0x00
                ends = characters
            else:
                begins = 0x20
                ends = characters + 0x20

            for char in [ord(char) for char in message]:
                if begins <= char <= ends:
                    file.seek((char-begins+1)*2)
                    file.seek(int.from_bytes(file.read(2), 'little'))
                    length = ord(file.read(1))
                    left, right = file.read(2)

                    left -= 0x52
                    right -= 0x52
                    width += (right - left) * scale
        return width

    # pylint: disable-msg=too-many-locals
    def draw(
            self,
            message,
            start_x=0,
            start_y=32,
            color=st7789.WHITE,
            font="/fonts/romant.fnt",
            scale=1):
        '''
        Draw message on the LCD display at the given location in specified
        font.

        Args:
            message (str): The message to write
            start_x (int): column to start at, defaults to 0
            start_y int): row to start at, defaults to 32
            font_file (str): The Hershy font file to use, defaults to romant.fnt
        '''
        from_x = to_x = pos_x = start_x
        from_y = to_y = pos_y = start_y
        penup = True

        with open(font, "rb", buffering=0) as file:
            characters = int.from_bytes(file.read(2), 'little')
            if characters > 96:
                begins = 0x00
                ends = characters
            else:
                begins = 0x20
                ends = characters + 0x20

            for char in [ord(char) for char in message]:
                if begins <= char <= ends:
                    file.seek((char-begins+1)*2)
                    file.seek(int.from_bytes(file.read(2), 'little'))
                    length = ord(file.read(1))
                    left, right = file.read(2)

                    left -= 0x52            # Position left side of the glyph
                    right -= 0x52           # Position right side of the glyph
                    width = right - left    # Calculate the character width

                    for vect in range(length):
                        vector_x, vector_y = file.read(2)
                        vector_x -= 0x52
                        vector_y -= 0x52

                        if vector_x == -50:
                            penup = True
                            continue

                        vector_x *= scale
                        vector_y *= scale

                        if not vect or penup:
                            from_x = pos_x + vector_x - left
                            from_y = pos_y + vector_y

                        else:
                            to_x = pos_x + vector_x - left
                            to_y = pos_y + vector_y

                            self.display.line(
                                from_x,
                                from_y,
                                to_x,
                                to_y,
                                color)

                            from_x = to_x
                            from_y = to_y

                        penup = False

                    pos_x += width * scale

    def character(self, char, col=0, line=0, fg=None, bg=None):
        """
        Write a character using the fg and bg colors.

        Args:
            char (int): Char to write at location
            col (optional int): column to write at (defaults to 0)
            line (int): Line number to write on (defaults to 0)
            fg (int): 565 color for character forground
            bg (int): 565 color for character background
        """
        if fg is None:
            fg = self.fg
        if bg is None:
            bg = self.bg

        x_offset = col * self.font.WIDTH
        y_offset = line * self.font.HEIGHT

        self.display.fill_rect(
            x_offset,
            y_offset,
            self.font.WIDTH,
            self.font.HEIGHT,
            bg)

        self.display.text(font, chr(char), x_offset, y_offset, fg, bg)

    def write(self, txt, col=0, line=0, fg=None, bg=None):
        """
        Clear the bg and write txt using the fg color.

        Args:
            txt (str): Text to write to line
            col (int): Column to start writing at
            line (int): Line number to write on
            fg (int): 565 color for character forground
            bg (int): 565 color for character background
        """
        if fg is None:
            fg = self.fg
        if bg is None:
            bg = self.bg

        x_offset = col * self.font.WIDTH
        y_offset = line * self.font.HEIGHT
        self.display.fill_rect(
            x_offset,
            y_offset,
            self.font.WIDTH*len(txt),
            self.font.HEIGHT,
            bg)

        self.display.text(
            self.font,
            txt,
            x_offset,
            y_offset,
            fg,
            bg)

    def writeln(self, txt, col=0, line=0, fg=None, bg=None):
        """
        Set the entire line of the display to the bg color then write
        txt using the fg color.

        Args:
            txt (str): Text to write to line
            col (optional int): Column to start writing at
            line (int): Line number to write on
            fg (int): 565 color for character forground
            bg (int): 565 color for character background
        """
        if fg is None:
            fg = self.fg
        if bg is None:
            bg = self.bg

        x_offset = col * self.font.WIDTH
        y_offset = line*self.font.HEIGHT
        self.display.fill_rect(
            0,
            y_offset,
            self.width,
            self.font.HEIGHT,
            bg)

        self.display.text(self.font, txt, x_offset, y_offset, fg, bg)

    def center(self, txt, line=0, fg=None, bg=None):
        """
        Set the entire line of the display to the bg color then write
        txt centered on the line using the fg color.

        Args:
            txt (str): Text to write to line
            line (int): Line number to write on
            fg (int): 565 color for character forground
            bg (int): 565 color for character background
        """
        if fg is None:
            fg = self.fg
        if bg is None:
            bg = self.bg

        self.writeln(txt.center(self.max_chars), 0, line, fg, bg)

    def cls(self, txt=None, line=0, fg=None, bg=None):
        """
        cls - clear screen optionally centering text on line

        Args:
            txt (optional string): text to center on line
            line (optional int): line to write on
            fg (int): 565 color for character forground
            bg (int): 565 color for character background
        """
        if fg is None:
            fg = self.fg
        if bg is None:
            bg = self.bg

        self.display.fill(bg)
        if txt:
            self.center(txt, line, fg, bg)

    def wait(self, text, line=0, fg=None, bg=None):
        """
        Clear entire line to bg color then write text centered on line
        in forground color then wait for any button to be pressed and released

        Args:
            txt (str): text to write to line
            line (int): line to write on
            fg (int): 565 color for character forground
            bg (int): 565 color for character background

        Returns:
            int: button pressed

        """
        if fg is None:
            fg = self.fg
        if bg is None:
            bg = self.bg

        self.center(text, line, fg, bg)
        return self.joystick.read()

    def underline(self, col, line, width, fg=None, bg=None):
        """
        underline - draw underline on line starting at col for width characters

        Args:
            line (int): line to draw on
            col (int): character position to start at
            width (int): number of underlines to draw
            reverse (optional bool): true reverse forground and bg colors
        """
        if fg is None:
            fg = self.fg
        if bg is None:
            bg = self.bg

        w = width*self.font.WIDTH
        if w+col > self.display.width():
            w = self.display.width() - col

        self.display.hline(
            col*self.font.HEIGHT,
            (line+1)*self.font.HEIGHT-1,
            w,
            self.fg)

    def menu(self, title, menu, active=None, menu_text=None):
        """
        show menu and return user selection

        ====== ===============================
        Button Action
        ====== ===============================
        UP     moves to the previous menu item
        DOWN   moves to the next menu item
        CENTER selects the current menu item
        RIGHT  selects the current menu item
        LEFT   Cancels and exits menu
        ====== ===============================

        ====== ===============================
        Button Long Press Action
        ====== ===============================
        UP     moves to the first menu item
        DOWN   moves to the last menu item
        ====== ===============================

        Args:
            menu (list): list of menu items active (int): currently active
            menu option menu_text (optional int): item to use as menu text if
            the menu list contains a list or tuple

        Returns:
            The index number of the option that was selected or None if
            the right button was pressed.

        Example::

            main_menu =[
                ("Option1", test_func1),
                ("Option2", test_func2),
                ("Option3", test_func3),
                ("Exit",    0)
            ]

            selected = ui.menu("Main Menu, 0)

        Example using optional menu_text::

            # sta_if.scan() returns:
            #    Array of tuples
            #        (ssid, bssid, channel, RSSI, authmode, hidden)
            #
            # To make a menu of the SSID's to connect to:
            #
            scan = sta_if.scan()
            connect = ui.menu("Select AP", scan, connect, 0)
        """
        menu_count = len(menu)

        # adjust first if the current option would be off the screen
        current = 0 if active is None else active
        first_shown = current-self.max_lines+2 if current > self.max_lines-2 else 0

        self.cls()
        self.center(title, 0, self.fg_hdr, self.bg_hdr)

        # display the menu on line 2 thru max_lines-1
        while True:
            for line in range(self.max_lines-1):
                menu_item = first_shown + line
                if menu_item < menu_count:
                    self.writeln(
                        menu[menu_item] if menu_text is None
                        else menu[menu_item][menu_text],
                        0,
                        line+1,
                        self.fg_act if menu_item == current else self.fg,
                        self.bg_act if menu_item == current else self.bg)

            # wait for button to be pressed and released
            btn = self.joystick.read()
            # move up one menu item if possible
            if btn == button.UP:
                if current > 0:
                    current -= 1
                    if current < first_shown:
                        first_shown -= 1

            # move down one menu item if possible
            elif btn == button.DOWN:
                if current < menu_count-1:
                    current += 1
                    if current >= self.max_lines -1:
                        first_shown = current - self.max_lines+2

            # move to first menu item
            if btn == -button.UP:
                current = 0
                first_shown = 0

            # move to last menu item
            elif btn == -button.DOWN:
                current = menu_count
                first_shown = current - self.max_lines+1

            # return menu item value one was selected
            elif btn in (button.CENTER, button.RIGHT):
                return current

            # return None if canceled by left button
            elif btn in (button.LEFT, -button.LEFT):
                return None

    def input(self, label, max_len, value, kbd=None, header=None):
        """
        Single field input using onscreen keyboard

        Args:
            label (str): Label to display
            max_len (int): Maximum value length
            value (str): Field value
            kbd (optional list): list of strings defining keyboard
            header (optional str): header shown at top of display

        Returns:
            The the button used to exit and the string value

        ====== ==================================================
        Button Action
        ====== ==================================================
        UP     moves highlighted key up one row
        DOWN   moves highlighted key down one row
        RIGHT  moves highlighted key right
        LEFT   moves highlighted key left
        CENTER selects highlighted key
        UPPER  changes keyboard (uppercase, lowercase, numbers..)
        LOWER  same as enter key, exits field
        ====== ==================================================

        The left faceing arrow (<-) is the backspace key.
        The hollow triangle is the enter key that exits the field.
        The space between these two keys is used as the spacebar.

        """
        if kbd is None:
            kbd = ALNUM

        active_kbd = 0
        kbd_count = len(kbd)
        lines_count = len(kbd[active_kbd])
        lengths = [0] * lines_count
        columns = [0] * lines_count
        rows = [64+line*self.font.HEIGHT for line in range(lines_count)]
        active_row = 0
        active_col = 0
        blink = False

        if isinstance(value, (int, float)):
            value = str(value)

        length = len(value)
        current = length

        def show_kbd():
            """
            Clear the tft and display the label and current field value
            then set the lengths and columns values for the active_kbd and
            display the keyboard.
            """
            self.cls()

            if header is not None:
                self.center(header, 0, self.fg_hdr, self.bg_hdr)

            self.writeln(label, 0, 1)
            self.writeln(value, 0, 2)
            self.underline(0, 2, max_len)

            for line_idx, kb_line in enumerate(kbd[active_kbd]):
                lengths[line_idx] = len(kbd[active_kbd][line_idx])
                columns[line_idx] = self.width//2-lengths[line_idx]*(self.font.WIDTH)//2

                for chr_idx, char in enumerate(kb_line):
                    self.display.text(
                        self.font,
                        char,
                        columns[line_idx]+chr_idx*self.font.WIDTH,
                        rows[line_idx],
                        self.fg,
                        self.bg
                    )

        def show_key(fg, bg):
            """
            Show the active_row and active_col key for the active_kdb in
            the specified fg and bg colors.
            """
            self.display.text(
                self.font,
                kbd[active_kbd][active_row][active_col],
                columns[active_row]+active_col*self.font.WIDTH,
                rows[active_row],
                fg,
                bg
            )

        def move_key(row, col):
            """
            Set the active_row and active_col to the specified row and col.
            Limits active_row and active_col to valid values.
            """
            nonlocal active_row, active_col
            active_row = row
            active_row %= lines_count

            active_col = col
            if active_col > lengths[active_row]:
                active_col = lengths[active_row]-1
            active_col %= lengths[active_row]

        def change_active_kbd(direction=1):
            """
            Make the next kbd the active_kdb then display it.
            """
            nonlocal active_kbd, active_row, active_col
            active_kbd += direction
            active_kbd %= kbd_count
            show_kbd()
            move_key(active_row, active_col)

        def show_char(char):
            """
            """
            self.display.text(
                self.font,
                char,
                current*self.font.WIDTH,
                2*self.font.HEIGHT,
                self.fg,
                self.bg
            )
            self.underline(current, 2, 1)

        def backspace_char():
            nonlocal current, value
            if current:
                show_char(" ")
                value = value[:-1]
                current -= 1

        def append_char(char):
            nonlocal current, value
            if current < max_len:
                show_char(char)
                value += char
                current += 1

        show_kbd()

        while True:
            show_key(self.fg_act, self.bg_act)
            btn = self.joystick.read(500)
            if btn != 0:
                show_key(self.fg, self.bg)

                if btn == button.CENTER:
                    char = ord(kbd[active_kbd][active_row][active_col])
                    if char == 0x7f:
                        return (btn, value)
                    elif char == 0x001b:
                        backspace_char()
                    else:
                        append_char(chr(char))

                elif btn == -button.UP:
                    change_active_kbd(-1)
                elif btn in [-button.DOWN, button.CHANGE]:
                    change_active_kbd(1)
                elif btn == button.UP:
                    move_key(active_row-1, active_col)
                elif btn == button.DOWN:
                    move_key(active_row+1, active_col)
                elif btn == button.LEFT:
                    move_key(active_row, active_col-1)
                elif btn == button.RIGHT:
                    move_key(active_row, active_col+1)
                elif btn in [button.ENTER, -button.ENTER]:
                    return (btn, value)

            self.display.fill_rect(
                current*self.font.WIDTH,
                2*self.font.HEIGHT,
                self.font.WIDTH,
                self.font.HEIGHT-1,
                self.bg if blink else self.fg)

            blink = not blink

    def select(self, column, line, options, value):
        """
        select -

        Args:
            column (int): First column of field
            line (int): Line to show input field on
            options (list): list of options
            value (int): index of initial selected option

        Returns:
            tuple (exit, value)
                exit: exit button
                value: value as a integer

        ====== ==========================================
        Button Action
        ====== ==========================================
        UP     exits selection field
        DOWN   exits selection field
        LEFT   move cursor to previous choice
        RIGHT  move cursor to the next choice
        CENTER exits and returns current selection
        ====== ==========================================

        """
        btn = 0
        option_count = len(options)
        while btn not in (button.CENTER, button.UP, button.DOWN):
            location = column
            for num, option in enumerate(options):
                self.write(
                    option,
                    location,
                    line,
                    self.fg_act if num == value else self.fg,
                    self.bg_act if num == value else self.bg)

                location += len(option)+1

            btn = self.joystick.read()

            if btn == button.LEFT:
                value -= 1
                value %= option_count

            if btn == button.RIGHT:
                value += 1
                value %= option_count

        return (btn, value)

    def _head(self, active, init, params): # pylint: disable-msg=unused-argument
        """
        _head helper

        [0, "Stars"]
        0: line
        1: text
        """
        line, text = params
        self.center(text, line, self.fg_hdr, self.bg_hdr)
        return False

    def _center(self, active, init, params): # pylint: disable-msg=unused-argument
        """
        _center helper

        [0, "Stars"]
        """
        line, text = params
        self.center(text, line)
        return False

    def _string(self, active, init, params, header=None):
        """
        _string helper

        [l_col, l_line, label, col, line, max_len, value]

        """
        l_column, l_line, label, column, line, max_length, value = params

        if init:
            self.write(label, l_column, l_line)

            self.write(
                '{:<{width}}'.format(value[:max_length], width=max_length-1),
                column,
                line,
                self.fg_act if active else self.fg,
                self.bg_act if active else self.bg
            )

            self.underline(column, line, max_length)
            return True

        btn, value =  self.input(label, max_length, value, header=header)
        return (btn, value)

    def _integer(self, active, init, params, header=None):
        """
        _integer helper

        [l_col, l_line, label, col, line, max_len, value]
        """
        l_column, l_line, label, column, line, max_length, value = params
        s_value = str(value)

        if init:
            self.write(label, l_column, l_line)

            self.write(
                '{:<{width}}'.format(s_value[:max_length], width=max_length),
                column,
                line,
                self.fg_act if active else self.fg,
                self.bg_act if active else self.bg
            )

            self.underline(column, line, max_length)
            return True

        btn, s_value = self.input(label, max_length, s_value, NUM, header=header)
        value = int(s_value)

        return (btn, int(value))

    def _text(self, active, init, params): # pylint: disable-msg=unused-argument
        """
        _text helper

        [0, 4, "Length:"],
        """
        line, column, text = params
        self.write(text, column, line)
        return False

    def _select(self, active, init, params, header=None):
        """
        _select helper

            with label:
                [0, 5, "Scale:", 6, 5, ("1", "2", "3"), scale]

             without label:
                [0, 5, ("1", "2", "3"), scale]

        """

        if len(params) == 7:
            l_col, l_line, label, col, line, options, value = params
        else:
            l_col, l_line, label = None, None, None
            col, line, options, value =  params

        if init:
            if label is not None:
                self.write(
                    label,
                    l_col,
                    l_line,
                    self.fg_act if active else self.fg,
                    self.bg_act if active else self.bg)

            location = col
            for num, option in enumerate(options):
                self.write(
                    option,
                    location,
                    line,
                    self.bg if num == value else self.fg,
                    self.fg if num == value else self.bg)
                location += len(option)+1
            return True

        if label is not None:
            self.write(label, l_col, l_line, self.fg, self.bg)

        return self.select(col, line, options, value)

    def _ok(self, active, init, params, header=None):
        return self._select(active, init, params, header)

    # Form item type constants
    HEAD = _head
    CENTER = _center
    STR = _string
    INT = _integer
    TEXT = _text
    SEL = _select
    OK = _ok

    FUN = const(0)
    VAL = const(7)
    FLD = const(0)

    def form(self, items, line=7):
        """
        Display a form created from a list of field definitions and allow the
        user to edit it.

        Args:
            items (list): list of form items
            line (int): line to show Accept / Cancel selection on exit

        Returns
            Bool: True if Accept selected, False if Cancel selected on exit.
            Defaults to line 7

        ====== ==========================================
        Button Action
        ====== ==========================================
        CENTER Next field
        ====== ==========================================

        ====== ==========================================
        Button Long Press Action
        ====== ==========================================
        CENTER Exit form
        LEFT   Previous field
        RIGHT  Next field
        ====== ==========================================

        **Field Definitions**

        **HEAD:**

            Display text on line centered with forground and bg colors
            reversed.

            Parameters
                [HEAD, line, text]

            =========== ==========================
            Parameter   Description
            =========== ==========================
            HEAD        Create `header` field
            line        Line to display field on
            text        Text to display
            =========== ==========================

        **CENTER:**

            Parameters
                [CENTER, line, text]

                ===== =========== ========================
                Index Parameter   Description
                ===== =========== ========================
                    0 CENTER      Create `center` field
                    1 line        Line to display field on
                    2 text        Text to display
                ===== =========== ========================

        **STR:**

            Parameters
                [uio.STR, l_col, l_line, label, col, line, max_len, value]

            ===== =========== =========================
            Index Parameter   Description
            ===== =========== =========================
                0 STR         Create `string` field
                1 l_column    Label column
                2 l_line      Label line
                3 label       Label text
                4 column      Field column
                5 line        Field line
                6 max_length  Field max length
                7 value       Value of field
            ===== =========== =========================

        **INT:**

            Parameters
                [uio.INT, l_col, l_line, label, col, line, max_len, value]

            ===== =========== =========================
            Index Parameter   Description
            ===== =========== =========================
                0 INT         Create `int` field
                1 l_line      Label line
                2 l_column    Label column
                3 label       Label text
                4 column      Field column
                5 line        Field line
                6 max_length  Field max length
                7 value       Value of field
            ===== =========== =========================

        **TEXT:**

            Parameters
                [TEXT, column, line, text]

            ===== =========== =========================
            Index Parameter   Description
            ===== =========== =========================
                1 TEXT        Create `text` field
                2 column      Column to display field at
                3 line        Line to display field on
                4 text        Text to display
            ===== =========== =========================

        **SEL:**

            Parameters without label:
                [SEL, column, line, [selection_list] , selected]

            ===== ================ ==========================
            Index Parameter        Description
            ===== ================ ==========================
                0 SEL              Create `selection` field
                1 column           Column to display field at
                2 line             Line to display field on
                3 [selection_list] List of strings to select
                4 selected         Currently selected string
            ===== ================ ==========================

            Parameters with label:
                [SEL, l_column, l_line, label, column, line, [selection_list], selected]

            ===== ================ ==========================
            Index Parameter        Description
            ===== ================ ==========================
                0 SEL              Create `selection` field
                1 l_column         Column to display label on
                2 l_line           Line to display label on
                3 label            Label to display
                4 column           Column to display field at
                5 line             Line to display field on
                6 [selection_list] List of strings to select
                7 selected         Currently selected string
            ===== ================ ==========================

        **OK:**

            Parameters
                [OK, column, line, [selection_list] , selected]

            ===== ================ ==========================
            Index Parameter        Description
            ===== ================ ==========================
                0 OK               Create `OK` field
                1 column           Column to display field at
                2 line             Line to display field on
                3 [selection_list] List of strings to select
                4 selected         Currently selected string
            ===== ================ ==========================

        """

        self.cls()
        header = None
        fields = []
        for num, item in enumerate(items):
            if callable(item[self.FUN]):
                if (item[self.FUN].__name__ == "_head"):
                    header = item[2]

                if (item[self.FUN].__name__ not in ["_text", "_head", "_center"]):
                    fields.append(num)

        field_count = len(fields)
        current = 0
        btn = 0

        while btn not in (button.ENTER, -button.ENTER):
            self.cls()
            was_ok = False
            index = 0

            for num, item in enumerate(items):
                if callable(item[self.FUN]):
                    if item[self.FUN].__name__ == "_ok":
                        if index == current:
                            was_ok = True
                            btn, value = item[self.FUN](index == current, False, item[1:])
                            if btn == button.CENTER:
                                return (btn, value)

                    if item[self.FUN](index == current, True, item[1:]):
                        index += 1

            if not was_ok:
                btn = self.joystick.read()

            if btn == button.CENTER:
                field = items[fields[current]][self.FLD]
                btn, value = field(False, False, items[fields[current]][1:], header)
                items[fields[current]][self.VAL] = value

            if btn == button.UP:
                current -= 1
                current %= field_count

            if btn in [button.DOWN, 0x7f]:
                current += 1
                current %= field_count

        return (btn, value)
