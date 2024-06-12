import enum
import unicodedata


__all__ = [
    'BoxChar',
    'BoxCanvas'
]


class BoxChar(enum.Flag, boundary=enum.KEEP):
    SPACE = 0
    #
    LEFT = 1
    UP = 2
    RIGHT = 4
    DOWN = 8
    #
    SINGLE_MASK = 0x0F
    #
    LEFT_DOUBLE = 1 + 16
    UP_DOUBLE = 2 + 32
    RIGHT_DOUBLE = 4 + 64
    DOWN_DOUBLE = 8 + 128
    #
    DOUBLE_MASK = 0xF0
    #
    HORIZONTAL = LEFT | RIGHT
    VERTICAL = UP | DOWN
    #
    DOWN_AND_RIGHT = DOWN | RIGHT
    DOWN_AND_LEFT = DOWN | LEFT
    UP_AND_RIGHT = UP | RIGHT
    UP_AND_LEFT = UP | LEFT
    #
    VERTICAL_AND_RIGHT = VERTICAL | RIGHT
    VERTICAL_AND_LEFT = VERTICAL | LEFT
    DOWN_AND_HORIZONTAL = DOWN | HORIZONTAL
    UP_AND_HORIZONTAL = UP | HORIZONTAL
    #
    VERTICAL_AND_HORIZONTAL = VERTICAL | HORIZONTAL
    #
    DOUBLE_HORIZONTAL = LEFT_DOUBLE | RIGHT_DOUBLE
    DOUBLE_VERTICAL = UP_DOUBLE | DOWN_DOUBLE
    #
    DOWN_SINGLE_AND_RIGHT_DOUBLE = DOWN | RIGHT_DOUBLE
    DOWN_DOUBLE_AND_RIGHT_SINGLE = DOWN_DOUBLE | RIGHT
    DOUBLE_DOWN_AND_RIGHT = DOWN_DOUBLE | RIGHT_DOUBLE
    #
    DOWN_SINGLE_AND_LEFT_DOUBLE = DOWN | LEFT_DOUBLE
    DOWN_DOUBLE_AND_LEFT_SINGLE = DOWN_DOUBLE | LEFT
    DOUBLE_DOWN_AND_LEFT = DOWN_DOUBLE | LEFT_DOUBLE
    #
    UP_SINGLE_AND_RIGHT_DOUBLE = UP | RIGHT_DOUBLE
    UP_DOUBLE_AND_RIGHT_SINGLE = UP_DOUBLE | RIGHT
    DOUBLE_UP_AND_RIGHT = UP_DOUBLE | RIGHT_DOUBLE
    #
    UP_SINGLE_AND_LEFT_DOUBLE = UP | LEFT_DOUBLE
    UP_DOUBLE_AND_LEFT_SINGLE = UP_DOUBLE | LEFT
    DOUBLE_UP_AND_LEFT = UP_DOUBLE | LEFT_DOUBLE
    #
    VERTICAL_SINGLE_AND_RIGHT_DOUBLE = VERTICAL | RIGHT_DOUBLE
    VERTICAL_DOUBLE_AND_RIGHT_SINGLE = DOUBLE_VERTICAL | RIGHT
    DOUBLE_VERTICAL_AND_RIGHT = DOUBLE_VERTICAL | RIGHT_DOUBLE
    #
    VERTICAL_SINGLE_AND_LEFT_DOUBLE = VERTICAL | LEFT_DOUBLE
    VERTICAL_DOUBLE_AND_LEFT_SINGLE = DOUBLE_VERTICAL | LEFT
    DOUBLE_VERTICAL_AND_LEFT = DOUBLE_VERTICAL | LEFT_DOUBLE
    #
    DOWN_SINGLE_AND_HORIZONTAL_DOUBLE = DOWN | DOUBLE_HORIZONTAL
    DOWN_DOUBLE_AND_HORIZONTAL_SINGLE = DOWN_DOUBLE | HORIZONTAL
    DOUBLE_DOWN_AND_HORIZONTAL = DOWN_DOUBLE | DOUBLE_HORIZONTAL
    #
    UP_SINGLE_AND_HORIZONTAL_DOUBLE = UP | DOUBLE_HORIZONTAL
    UP_DOUBLE_AND_HORIZONTAL_SINGLE = UP_DOUBLE | HORIZONTAL
    DOUBLE_UP_AND_HORIZONTAL = UP_DOUBLE | DOUBLE_HORIZONTAL
    #
    VERTICAL_SINGLE_AND_HORIZONTAL_DOUBLE = VERTICAL | DOUBLE_HORIZONTAL
    VERTICAL_DOUBLE_AND_HORIZONTAL_SINGLE = DOUBLE_VERTICAL | HORIZONTAL
    DOUBLE_VERTICAL_AND_HORIZONTAL = DOUBLE_VERTICAL | DOUBLE_HORIZONTAL

    @property
    def unicode_name(self):
        """
        Get the unicode character name corresponding to this value.

        Note that some values will return a name that does not correspond to a valid unicode character.
        In particular: DOUBLE_RIGHT, DOUBLE_UP, etc., since these were not included in the box drawings block.
        """
        if self == BoxChar.SPACE:
            return 'SPACE'
        #
        name = 'BOX DRAWINGS '
        if (self & BoxChar.VERTICAL_AND_HORIZONTAL) == self:
            name += 'LIGHT '
        name += self.name.replace('_', ' ')
        return name

    def __str__(self):
        """
        Look up and return the unicode character corresponding to this value.
        If not found (unicodedata.lookup throws a KeyError), then the unicode replacement character will be returned.
        """
        try:
            return unicodedata.lookup(self.unicode_name)
        except KeyError:
            return '�'


class BoxCanvas:
    def __init__(self):
        self._width = 0
        self._height = 0
        self._canvas: list[BoxChar | str | None] = []

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def __getitem__(self, index):
        x, y = index
        if 0 <= x < self.width and 0 <= y < self.height:
            return self._canvas[y][x]

    def __setitem__(self, index, value):
        x, y = index
        if x < 0 or y < 0:
            return
        self.expand(x + 1, y + 1)
        self._canvas[y][x] = value

    def __str__(self):
        text = ''
        for row in self._canvas:
            for cell in row:
                if cell is None:
                    text += ' '
                else:
                    text += str(cell)
            text += '\n'
        return text

    def expand(self, w, h):
        if w > self.width:
            for row in self._canvas:
                row += [None] * (w - self.width)
            self._width = w
        if h > self.height:
            for _ in range(h - self.height):
                self._canvas.append([None] * self.width)
            self._height = h

    def or_boxchar(self, x, y, item: BoxChar):
        current = self[x, y]
        if isinstance(current, BoxChar):
            self[x, y] = current | item
        elif current is None:
            self[x, y] = item

    def and_boxchar(self, x, y, item: BoxChar):
        current = self[x, y]
        if isinstance(current, BoxChar):
            self[x, y] = current & item

    def remove_boxchar(self, x, y, item: BoxChar):
        self.and_boxchar(x, y, ~item)

    def draw_horizontal(self, x, y, w, double: bool = False):
        right = BoxChar.RIGHT_DOUBLE if double else BoxChar.RIGHT
        left = BoxChar.LEFT_DOUBLE if double else BoxChar.LEFT
        for x_ in range(x, x + w - 1):
            self.or_boxchar(x_, y, right)
            self.or_boxchar(x_ + 1, y, left)

    def draw_vertical(self, x, y, h, double: bool = False):
        down = BoxChar.DOWN_DOUBLE if double else BoxChar.DOWN
        up = BoxChar.UP_DOUBLE if double else BoxChar.UP
        for y_ in range(y, y + h - 1):
            self.or_boxchar(x, y_, down)
            self.or_boxchar(x, y_ + 1, up)

    def clear_rect(self, x, y, w, h):
        left = max(0, x)
        right = min(self.width, x + w)
        top = max(0, y)
        bottom = min(self.height, y + h)
        for x_ in range(left, right):
            for y_ in range(top, bottom):
                self[x_, y_] = None

    def clear_box(self, x, y, w, h):
        self.clear_rect(x + 1, y + 1, w - 2, h - 2)
        for x_ in range(x, x + w):
            self.remove_boxchar(x_, y, BoxChar.DOWN_DOUBLE)
            self.remove_boxchar(x_, y + h - 1, BoxChar.UP_DOUBLE)
        for y_ in range(y, y + h):
            self.remove_boxchar(x, y_, BoxChar.RIGHT_DOUBLE)
            self.remove_boxchar(x + w - 1, y_, BoxChar.LEFT_DOUBLE)

    def draw_box(self, x, y, w, h,
                 double_top: bool = False,
                 double_bottom: bool = False,
                 double_left: bool = False,
                 double_right: bool = False,
                 double_all: bool = False,
                 fill: bool = False,
                 ):
        if fill:
            self.clear_box(x, y, w, h)
        self.draw_horizontal(x, y, w, double_top or double_all)
        self.draw_horizontal(x, y + h - 1, w, double_bottom or double_all)
        self.draw_vertical(x, y, h, double_left or double_all)
        self.draw_vertical(x + w - 1, y, h, double_right or double_all)

    def text_box(self, x, y, text, pad_left=1, pad_right=1, **kwargs):
        lines = text.splitlines()
        w = max(map(len, lines)) + 2 + pad_left + pad_right
        h = len(lines) + 2
        self.draw_box(x, y, w, h, fill=True, **kwargs)
        for r, line in enumerate(lines):
            for c, char in enumerate(line):
                self[x + pad_left + c + 1, y + r + 1] = char
