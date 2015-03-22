import re
import pytest
from tabipy import Table, TableHeaderRow, TableCell

@pytest.fixture
def t():
    "Returns the table used in the col_span tests"
    t = Table((1,2,3),
              (4,5,6),
              (7,8,9))
    cell_1_1 = t.rows[0].cells[0]
    cell_1_1.col_span = 2
    return t

def test_col_span_html(t):
    "This test col_span works in html"
    t1_html = t._repr_html_()
    row_split = re.compile('<\s*tr\s*>')
    lines = row_split.split(t1_html)
    assert len(lines)==4
    col_split = re.compile('>[\s\d\s]*<')
    parts = col_split.split(lines[1])
    cl_check = re.compile('colspan\s*=\s*"\s*2\s*"')
    assert len(cl_check.findall(parts[0]))>0
    #print("pass")

def test_col_span_latex(t):
    "This test col_span works in latex"
    t1_latex = t._repr_latex_()
    row_split = re.compile(r'\\\\')
    lines = row_split.split(t1_latex)
    assert len(lines)==4
    col_split = re.compile('&')
    parts = col_split.split(lines[0])
    cl_check = re.compile('\w*\\multicolumn\s*\{\s*2\s*}')
    assert len(cl_check.findall(parts[0]))>0
    #print("pass")

def test_col_span_format():
    t = Table(TableHeaderRow('A', 'B', 'C', 'D',
                             col_format=('{:.2g}', '{:3g}', '{:d}', '{:10.4g}')),
              (1.50, TableCell(3.5678, col_span=2), 10.9876),
              (112.679, 74.2974, 2.298639, 7.46036))
    cell_3_2 = t.rows[2].cells[1]
    cell_3_2.col_span = 2
    expected = (('A', 'B', 'C', 'D'),
                ('1.5', '3.57', '     10.99'),
                ('1.1e+02', '74.3', '      7.46'))

    t_html = t._repr_html_()
    row_split = re.compile('<\s*tr\s*>')
    col_split = re.compile(r'(?<=\>).*?(?=\<)')
    
    for row, row_exp in zip(row_split.split(t_html)[1:], expected):
        cells = [c for c in col_split.findall(row) if c]
        for cell, cell_exp in zip(c, row_exp):
             assert cell == cell_exp
