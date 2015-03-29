import re
import pytest
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
    t = Table(TableHeaderRow('A', 'B', 'C'), 
              (1.50, 2, 3.5678),
              (TableHeader('Total'), 20, 30),
              col_format=('{:.2g}', '{:d}', '{:10.4g}'))
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
    t = Table(TableHeaderRow('A', 'B', 'C'), 
              (1.50, 2, 3.5678),
              (TableHeader('Total'), 20, 30),
              col_format=('{:.2g}', '{:d}', '{:10.4g}'))
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

def test_col_format_wrong_count():
    with pytest.raises(ValueError) as excinfo:
        t = Table(TableHeaderRow('A', 'B', 'C'), 
                  (1.50, 2, 3.5678),
                  (TableHeader('Total'), 20, 30),
                  col_format=('{:.2g}', '{:d}')) 
    assert 'Wrong number of format strings' in str(excinfo)

    with pytest.raises(ValueError) as excinfo:
        t = Table(TableHeaderRow('A', 'B', 'C'), 
                  (1.50, 2, 3.5678),
                  (TableHeader('Total'), 20, 30),
                  col_format=('{:.2g}', '{:d}', '{:10.4g}', '{:f}')) 
    assert 'Wrong number of format strings' in str(excinfo)

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

def default_table():
    "Returns the unmodified base table for testing"
    t = Table((1,2,3),
    (4,5,6),
    (7,8,9))
    return t

def col_span_table():
    "Returns the table used in the col_span tests"
    t = default_table()
    cell_1_1 = t.rows[0].cells[0]
    cell_1_1.col_span = 2
    return t

def test_col_span_html():
    "This tests that col_span works in html"
    t = col_span_table()
    #actual_col_span_html(t)
    t1_html = t._repr_html_()
    row_split = re.compile('<\s*tr\s*>')
    lines = row_split.split(t1_html)
    assert len(lines)==4
    col_split = re.compile('>[\s\d\s]*<')
    parts = col_split.split(lines[1])
    cl_check = re.compile('colspan\s*=\s*"\s*2\s*"')
    assert len(cl_check.findall(parts[0]))>0
    
def _actual_col_span_html(t):
    "For testing at low level modifications and cell method"
    t1_html = t._repr_html_()
    row_split = re.compile('<\s*tr\s*>')
    lines = row_split.split(t1_html)
    assert len(lines)==4
    col_split = re.compile('>[\s\d\s]*<')
    parts = col_split.split(lines[1])
    cl_check = re.compile('colspan\s*=\s*"\s*2\s*"')
    assert len(cl_check.findall(parts[0]))>0
    #print("pass")

def test_col_span_latex():
    "This tests that col_span works in latex"
    t = col_span_table()  
    #actual_col_span_latex(t)
    t1_latex = t._repr_latex_()
    row_split = re.compile(r'\\\\')
    lines = row_split.split(t1_latex)
    assert len(lines)==4
    col_split = re.compile('&')
    parts = col_split.split(lines[0])
    cl_check = re.compile('\w*\\multicolumn\s*\{\s*2\s*}')
    assert len(cl_check.findall(parts[0]))>0
    
def _actual_col_span_latex(t):
    "For testing at low level modifications and cell method"
    t1_latex = t._repr_latex_()
    row_split = re.compile(r'\\\\')
    lines = row_split.split(t1_latex)
    assert len(lines)==4
    col_split = re.compile('&')
    parts = col_split.split(lines[0])
    cl_check = re.compile('\w*\\multicolumn\s*\{\s*2\s*}')
    assert len(cl_check.findall(parts[0]))>0
    #print("pass")
    
def cell_method_col_span_table():
    "Returns a table modified to test col_span using the cell method"
    t = default_table()
    t.cell(0, 0).col_span = 2
    return t
    
def test_cell_method_col_span_html():
    "This tests that col_span works in html"
    t = cell_method_col_span_table()
    t1_html = t._repr_html_()
    row_split = re.compile('<\s*tr\s*>')
    lines = row_split.split(t1_html)
    assert len(lines)==4
    col_split = re.compile('>[\s\d\s]*<')
    parts = col_split.split(lines[1])
    cl_check = re.compile('colspan\s*=\s*"\s*2\s*"')
    assert len(cl_check.findall(parts[0]))>0
    
def test_cell_method_col_span_latex():
    "This tests that col_span works in latex"
    t = cell_method_col_span_table()
    t1_latex = t._repr_latex_()
    row_split = re.compile(r'\\\\')
    lines = row_split.split(t1_latex)
    assert len(lines)==4
    col_split = re.compile('&')
    parts = col_split.split(lines[0])
    cl_check = re.compile('\w*\\multicolumn\s*\{\s*2\s*}')
    assert len(cl_check.findall(parts[0]))>0
