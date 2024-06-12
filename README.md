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
canvas.text_box(16, 1, 'Multi\nline\nbox')
print(canvas)
```

Output:
```text
┌────────┐                  
│       ┌┴──┐   ┌───────┐   
│       │   │   │ Multi │   
│  ╓────┤   ├───┤ line  │   
│  ║    ╘╤══╛   │ box   │   
│  ║ ╔═══╪════╗ └─────╥─┘   
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

Example:
```python
from boxxy import Table
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
```

Output:
```text
        ┌─────────┐                                
        │ Example │                                
        ├─────────┴────┬───────┬───────┐  ┌───────┐
        │ Col 1        │ Col 2 │ Col 3 │  │ Col 5 │
┌───────┼──────────────┼───────┴───────┴──┴───────┤
│ Row 1 │ Hello world! │                          │
└───────┼──────────────┼──────────────────────────┤
        │ Span         │ Span columns             │
┌───────┤ multiple     ├──────────────────────────┤
│ Row 3 │ rows         │                          │
└───────┴──────────────┴──────────────────────────┘
```
