import enum
import unicodedata
from dataclasses import dataclass

__all__ = [
    'BoxChar',
    'BoxCanvas',
    'TableCell',
    'Table',
]


class BoxChar(enum.Flag, boundary=enum.KEEP):
    SPACE = 0
    #
    LEFT = 1
    UP = 2
    RIGHT = 4
    DOWN = 8
    #
    LEFT_DOUBLE = 1 + 16
    UP_DOUBLE = 2 + 32
    RIGHT_DOUBLE = 4 + 64
    DOWN_DOUBLE = 8 + 128
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


class Padding:
    left: int
    up: int
    right: int
    down: int

    @property
    def width(self):
        return self.left + self.right

    @property
    def height(self):
        return self.up + self.down

    def __init__(self, *args: int):
        if len(args) == 0:
            self.left = self.up = self.right = self.down = 0
        elif len(args) == 1:
            self.left = self.up = self.right = self.down = args[0]
        elif len(args) == 2:
            self.left = self.right = args[0]
            self.up = self.down = args[1]
        elif len(args) == 4:
            self.left, self.up, self.right, self.down = args
        else:
            raise Exception(f'Padding() expects 0, 1, 2, or 4 arguments. Got {len(args)}.')


class BoxCanvas:
    default_padding: Padding = Padding(1, 0)

    def __init__(self):
        self._width = 0
        self._height = 0
        self._canvas: list[BoxChar | str | None] = []

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def __getitem__(self, index: tuple[int, int]) -> BoxChar | str | None:
        x, y = index
        if 0 <= x < self.width and 0 <= y < self.height:
            return self._canvas[y][x]

    def __setitem__(self, index: tuple[int, int], value: BoxChar | str | None):
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

    def expand(self, w: int, h: int):
        if w > self.width:
            for row in self._canvas:
                row += [None] * (w - self.width)
            self._width = w
        if h > self.height:
            for _ in range(h - self.height):
                self._canvas.append([None] * self.width)
            self._height = h

    def or_boxchar(self, x: int, y: int, item: BoxChar):
        current = self[x, y]
        if isinstance(current, BoxChar):
            self[x, y] = current | item
        elif current is None:
            self[x, y] = item

    def and_boxchar(self, x: int, y: int, item: BoxChar):
        current = self[x, y]
        if isinstance(current, BoxChar):
            self[x, y] = current & item

    def remove_boxchar(self, x: int, y: int, item: BoxChar):
        self.and_boxchar(x, y, ~item)

    def draw_horizontal(self, x: int, y: int, w: int, double: bool = False):
        right = BoxChar.RIGHT_DOUBLE if double else BoxChar.RIGHT
        left = BoxChar.LEFT_DOUBLE if double else BoxChar.LEFT
        for x_ in range(x, x + w - 1):
            self.or_boxchar(x_, y, right)
            self.or_boxchar(x_ + 1, y, left)

    def draw_vertical(self, x: int, y: int, h: int, double: bool = False):
        down = BoxChar.DOWN_DOUBLE if double else BoxChar.DOWN
        up = BoxChar.UP_DOUBLE if double else BoxChar.UP
        for y_ in range(y, y + h - 1):
            self.or_boxchar(x, y_, down)
            self.or_boxchar(x, y_ + 1, up)

    def clear_rect(self, x: int, y: int, w: int, h: int):
        left = max(0, x)
        right = min(self.width, x + w)
        top = max(0, y)
        bottom = min(self.height, y + h)
        for x_ in range(left, right):
            for y_ in range(top, bottom):
                self[x_, y_] = None

    def clear_box(self, x: int, y: int, w: int, h: int):
        self.clear_rect(x + 1, y + 1, w - 2, h - 2)
        for x_ in range(x, x + w):
            self.remove_boxchar(x_, y, BoxChar.DOWN_DOUBLE)
            self.remove_boxchar(x_, y + h - 1, BoxChar.UP_DOUBLE)
        for y_ in range(y, y + h):
            self.remove_boxchar(x, y_, BoxChar.RIGHT_DOUBLE)
            self.remove_boxchar(x + w - 1, y_, BoxChar.LEFT_DOUBLE)

    def draw_box(self,
                 x: int,
                 y: int,
                 w: int,
                 h: int,
                 *,
                 double_top: bool = False,
                 double_bottom: bool = False,
                 double_left: bool = False,
                 double_right: bool = False,
                 double_all: bool = False,
                 fill: bool = False,
                 ):
        """
        Draw a box.

        By default, this will be a single-line rectangle, but some or all edges may be drawn with doubled lines if
        specified via keyword arguments.

        By default, the inside of the box will be unmodified, meaning existing text will be left alone, and existing
        borders will be combined with the new ones. If :param:`fill` is set to true the inside will instead be filled with
        empty space, and existing borders will be adjusted to not continue into the box.

        :param x: X coordinate of upper left corner.
        :param y: Y coordinate of upper left corner.
        :param w: Width of box, including border.
        :param h: Height of box, including border.
        :param double_top: Draw the top edge with double lines.
        :param double_bottom: Draw the bottom edge with double lines.
        :param double_left: Draw the left edge with double lines.
        :param double_right: Draw the right edge with double lines.
        :param double_all: Draw all edges with double lines.
        :param fill: Fill the inside of the box with empty space.
        """
        if fill:
            self.clear_box(x, y, w, h)
        self.draw_horizontal(x, y, w, double_top or double_all)
        self.draw_horizontal(x, y + h - 1, w, double_bottom or double_all)
        self.draw_vertical(x, y, h, double_left or double_all)
        self.draw_vertical(x + w - 1, y, h, double_right or double_all)

    def fit_text(self, text, *, padding: Padding | None = None):
        """
        Figure out the size of the box required to fit around the given text.
        :param text: Text to be drawn.
        :param padding: Optional padding. Will use BoxCanvas.default_padding if None (the default).
        :return: A tuple (width, height) of the box that fits around the given text.
        """
        if padding is None:
            padding = self.default_padding
        lines = text.splitlines()
        w = max(map(len, lines)) + 2 + padding.width
        h = len(lines) + 2 + padding.height
        return w, h

    def text_box(self,
                 x: int,
                 y: int,
                 text: str,
                 *,
                 width: int | None = None,
                 height: int | None = None,
                 padding: Padding | None = None,
                 **kwargs
                 ) -> tuple[int, int]:
        """
        Draw a box with (left adjusted) text in it.

        If `width` and/or `height` is `None` (which is the default), then the missing value(s) will be calculated
        by `fit_text()`.

        If `width` and/or `height` is given, and the text extends outside the box, then the text will be clipped.

        :param x: X coordinate of upper left corner of the box.
        :param y: Y coordinate of upper left corner of the box.
        :param text: Text to be written inside the box.
        :param width: Width of the drawn box, including border and padding, or `None`.
        :param height: Height of the drawn box, including border and padding, or `None`.
        :param padding: Optional padding. Will use `default_padding` if `None` (the default).
        :param kwargs: Additional keyword arguments are passed to `draw_box()`.
        :returns: A tuple (width, height) of the final box size, including padding and borders.
        """

        if padding is None:
            padding = self.default_padding

        fit_w, fit_h = self.fit_text(text, padding=padding)
        if width is None:
            width = fit_w
        if height is None:
            height = fit_h

        self.draw_box(x, y, width, height, fill=True, **kwargs)

        lines = text.splitlines()
        for r, line in enumerate(lines):
            for c, char in enumerate(line):
                self[x + padding.left + c + 1, y + padding.up + r + 1] = char

        return width, height


@dataclass
class TableCell:
    row: int
    col: int
    content: any
    row_span: int = 1
    col_span: int = 1
    double: bool = False

    @property
    def left(self):
        return self.col

    @property
    def right(self):
        return self.col + self.col_span - 1

    @property
    def top(self):
        return self.row

    @property
    def bottom(self):
        return self.row + self.row_span - 1

    def contains_point(self, x: int, y: int) -> bool:
        return self.left <= x <= self.right and self.top <= y <= self.bottom

    def overlaps(self, other: 'TableCell') -> bool:
        return not (
            self.right < other.left or
            self.left > other.right or
            self.bottom < other.top or
            self.top > other.bottom
        )

    def __str__(self):
        x = str(self.col) if self.col_span == 1 else f'{self.col}:{self.col + self.col_span}'
        y = str(self.row) if self.row_span == 1 else f'{self.row}:{self.row + self.row_span}'
        return f'<R{x}, C{y}, "{self.content}">'


class Table:
    def __init__(self, title: str = ''):
        self.title = title
        self.cells: list[TableCell] = []
        self.row_headers: dict[int, str] = {}
        self.col_headers: dict[int, str] = {}
        self.width_overrides: dict[int, int] = {}
        self.height_overrides: dict[int, int] = {}

    @property
    def width(self):
        return max(
            max((cell.right + 1 for cell in self.cells), default=0),
            max((col + 1 for col, _ in self.col_headers.items()), default=0),
        )

    @property
    def height(self):
        return max(
            max((cell.bottom + 1 for cell in self.cells), default=0),
            max((row + 1 for row, _ in self.row_headers.items()), default=0),
        )

    def __getitem__(self, item: tuple[int, int]) -> TableCell | None:
        x, y = item
        for cell in self.cells:
            if cell.contains_point(x, y):
                return cell

    def __str__(self):
        canvas = BoxCanvas()
        self.draw(canvas)
        return str(canvas)

    def add_cell(self, new_cell: TableCell):
        for cell in self.cells:
            if cell.overlaps(new_cell):
                raise ValueError(f'Cell {new_cell} overlaps existing cell {cell}')
        self.cells.append(new_cell)

    def add(self, row: int, column: int, content: any, **kwargs):
        self.add_cell(TableCell(row, column, content, **kwargs))

    def draw(self, canvas: BoxCanvas, offset_x: int = 0, offset_y: int = 0):
        # Initialize an empty layout.
        # The default column and row size is 3, to fit a minimum box with a single empty character in it.
        col_widths = [3] * self.width
        row_heights = [3] * self.height
        # Optional items are sized to 1 by default, since 1 is subtracted in calculations.
        header_row_height = 1
        header_col_width = 1
        title_width, title_height = 1, 1

        # Figure out the minimum column widths and row heights to fit the table's content.
        for cell in self.cells:
            w, h = canvas.fit_text(cell.content)
            w //= cell.col_span
            h //= cell.row_span
            for c in range(cell.left, cell.right + 1):
                col_widths[c] = max(col_widths[c], w)
            for r in range(cell.top, cell.bottom + 1):
                row_heights[r] = max(row_heights[r], h)

        # Adjust layout to fit any given row or column headers.
        for c, text in self.col_headers.items():
            w, h = canvas.fit_text(text)
            col_widths[c] = max(col_widths[c], w)
            header_row_height = max(header_row_height, h)
        for r, text in self.row_headers.items():
            w, h = canvas.fit_text(text)
            row_heights[r] = max(row_heights[r], h)
            header_col_width = max(header_col_width, w)

        # Apply width and/or height overrides, if any have been set.
        for c, width in self.width_overrides.items():
            if c == -1:
                header_col_width = width
            else:
                col_widths[c] = width
        for r, height in self.height_overrides.items():
            if r == -1:
                header_row_height = height
            else:
                row_heights[r] = height

        # Compute the size of the title box.
        if len(self.title) > 0:
            title_width, title_height = canvas.fit_text(self.title)

        # Figure out the final coordinates of everything.
        title_x = offset_x + (header_col_width - 1)
        title_y = offset_y

        header_row_x = title_x
        header_row_y = title_y + (title_height - 1)

        header_col_x = offset_x
        header_col_y = header_row_y + (header_row_height - 1)

        x = header_row_x
        col_x = []
        for w in col_widths:
            col_x.append(x)
            x += w - 1
        col_x.append(x)

        y = header_col_y
        row_y = []
        for h in row_heights:
            row_y.append(y)
            y += h - 1
        row_y.append(y)

        # Now it's finally time to draw everything.
        canvas.draw_box(col_x[0], row_y[0], col_x[-1] - col_x[0] + 1, row_y[-1] - row_y[0] + 1, fill=True)

        if title_height > 2:
            canvas.text_box(title_x, title_y, self.title, width=title_width, height=title_height)

        if header_row_height > 2:
            for c, text in self.col_headers.items():
                canvas.text_box(col_x[c], header_row_y, text, width=col_widths[c], height=header_row_height)

        if header_col_width > 2:
            for r, text in self.row_headers.items():
                canvas.text_box(header_col_x, row_y[r], text, width=header_col_width, height=row_heights[r])

        for cell in self.cells:
            x = col_x[cell.left]
            y = row_y[cell.top]
            w = sum(col_widths[cell.left:cell.right + 1]) - cell.col_span + 1
            h = sum(row_heights[cell.top:cell.bottom + 1]) - cell.row_span + 1
            canvas.text_box(x, y, str(cell.content), width=w, height=h)


table = Table(title="Example")
table.row_headers[0] = 'Row 1'
table.row_headers[2] = 'Row 3'
table.col_headers[0] = 'Col 1'
table.col_headers[1] = 'Col 2'
table.col_headers[2] = 'Col 3'
table.col_headers[4] = 'Col 5'
table.add(0, 0, 'Hello world!')
table.add(1, 0, 'Span\nmultiple\nrows', row_span=2)
table.add(1, 1, 'Span columns', col_span=4)
print(table)
