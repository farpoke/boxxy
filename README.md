# boxxy
Provides utilities for drawing fancy text boxes and tables using the Unicode Box Drawings block.

---

Example:
```python
from boxxy import BoxCanvas
canvas = BoxCanvas()
canvas.draw_box(0, 0, 10, 10)
canvas.draw_box(5, 5, 10, 10, double_all=True)
canvas.draw_box(3, 3, 20, 8, double_left=True, double_right=True)
canvas.draw_box(8, 1, 5, 4, fill=True, double_bottom=True)
canvas.text_box(12, 9, 'Hello world!')
print(canvas)
```

Output:
```text
┌────────┐
│       ┌┴──┐
│       │   │
│  ╓────┤   ├─────────╖
│  ║    ╘╤══╛         ║
│  ║ ╔═══╪════╗       ║
│  ║ ║   │    ║       ║
│  ║ ║   │    ║       ║
│  ║ ║   │    ║       ║
└──╫─╫───┘  ┌─╨───────╨────┐
   ╙─╫──────┤ Hello world! │
     ║      └─╥────────────┘
     ║        ║
     ║        ║
     ╚════════╝
```

---
