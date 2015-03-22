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

def test_col_format():
    t = Table(TableHeaderRow('A', 'B', 'C', 
                             col_format=('{:.2g}', '{:d}', '{:10.4g}')),
              (1.50, 2, 3.5678),
              (TableHeader('Total'), 20, 30))
    expected = (('A', 'B', 'C'),
                ('1.5', '2', '     3.568'),
                ('Total', '20', '        30'))

#    for res_row, expected_row in zip(t.rows, expected):
#        for res_cell, expected_cell in zip(res_row.cells, expected_row):
#            # compare text surrounded by HTML tags
#            print res_cell._repr_html_()
#            assert re.search('(?<=>).*?(?=<)', 
#                             res_cell._repr_html_()).group() == expected_cell
#            # compare latex text, ignoring formatting for headers
#            assert res_cell._repr_latex_().split(r'\bf ')[-1] == expected_cell

    t_html = t._repr_html_()
    row_split = re.compile('<\s*tr\s*>')
    col_split = re.compile(r'(?<=\>).*?(?=\<)')

    for row, row_exp in zip(row_split.split(t_html)[1:], expected):
        cells = [c for c in col_split.findall(row) if c]
        for cell, cell_exp in zip(c, row_exp):
             assert cell == cell_exp


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
