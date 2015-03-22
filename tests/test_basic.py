import re
from tabipy import Table, TableRow, TableCell, TableHeaderRow, TableHeader

def test_simple():
    # For now, this is little more than a smoke test to check that it's not
    # erroring out.
    t = Table(TableHeaderRow('a','b','c'),
          (1,  2,  3),
          (2,  4,  6),
         )
    
    html = t._repr_html_()
    assert '<th' in html
    assert '<td' in html
    
    latex = t._repr_latex_()
    assert r'\hline' in latex

def test_tableheader():
    t = Table((TableHeader('a'), 1, 2),
              (TableHeader('b'), 3, 4),
              (TableHeader('c'), 5, 6))

    html = t._repr_html_()
    assert html.count('<th') == 3

    latex = t._repr_latex_()
    assert latex.count(r'\bf') == 3

def test_cell_format():
    inp_expected = (('{}', '1.6789'),
                    ('{:.4g}', '1.679'))

    # format set on creation
    for inp, expected in inp_expected:
        cell = TableCell(1.6789, format=inp)
        assert cell.formatted_value() == expected

    # format set after creation
    for inp, expected in inp_expected:
        cell = TableCell(1.6789)
        cell.format = inp
        assert cell.formatted_value() == expected

def test_col_format_html():
    t = Table(TableHeaderRow('A', 'B', 'C', 
                             col_format=('{:.2g}', '{:d}', '{:10.4g}')),
              (1.50, 2, 3.5678),
              (TableHeader('Total'), 20, 30))
    expected = (('A', 'B', 'C'),
                ('1.5', '2', '     3.568'),
                ('Total', '20', '        30'))

    t_html = t._repr_html_()
    row_split = re.compile('<\s*tr\s*>')
    col_split = re.compile(r'(?<=\>).*?(?=\<)')

    for row, row_exp in zip(row_split.split(t_html)[1:], expected):
        cells = [c for c in col_split.findall(row) if c]
        for cell, cell_exp in zip(cells, row_exp):
             assert cell == cell_exp

def test_col_format_latex():
    t = Table(TableHeaderRow('A', 'B', 'C', 
                             col_format=('{:.2g}', '{:d}', '{:10.4g}')),
              (1.50, 2, 3.5678),
              (TableHeader('Total'), 20, 30))
    expected = (('A', 'B', 'C'),
                ('1.5', '2', '     3.568'),
                ('Total', '20', '        30'))

    t_latex = t._repr_latex_()
    row_split = re.compile(r'\n')
    col_split = re.compile(r' & ')

    lines = row_split.split(t_latex)
    # check header
    for cell, cell_exp in zip(col_split.split(lines[2]), expected[0]):
        assert cell_exp in cell

    # check body
    for row, row_exp in zip(lines[4:-2], expected):
        cells = [c for c in col_split.split(row) if c]
        for cell, cell_exp in zip(cells, row_exp):
             assert cell_exp in cell

def test_escape():
    inp_expected = (('', ''),
                    ('&', r'\&'),
                    ('\\', r'{\textbackslash}'),
                    ('~', r'{\textasciitilde}'),
                    ('$', '\$'),
                    ('\n', r'{\linebreak}'),
                    ('\r', r'{\linebreak}'),
                    ('\r\n', r'{\linebreak}'),
                    ('_', r'\_'),
                    ('{', '\{'),
                    ('}', '\}'),
                    ('body & mind & r&d', r'body \& mind \& r\&d'),
                    (r'\_/~\_/', 
                     r'{\textbackslash}\_/{\textasciitilde}'
                     r'{\textbackslash}\_/'),
                    ('~_$\r\n{}', 
                     r'{\textasciitilde}\_\${\linebreak}\{\}'))
    for inp, expected in inp_expected:
        cell = TableCell(inp)
        assert cell._repr_latex_() == expected
