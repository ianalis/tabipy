import re
import pytest
from tabipy import Table, TableHeaderRow, TableCell

@pytest.fixture
def t():
    "Returns the table used in the col_span tests"
    t = Table((1,2,3),
              (4,5,6),
              (7,8,9))
    cell = t.cell(0,0)
    cell.row_span = 2
    return t

def test_row_span_html():
    "This test col_span works in html"
    t1_html = t()._repr_html_()
    row_split = re.compile('<\s*tr\s*>')
    lines = row_split.split(t1_html)
    assert len(lines)==4
    col_split = re.compile('>[\s\d\s]*<')
    row1_parts = col_split.split(lines[1])
    row2_parts = col_split.split(lines[2])
    cl_check = re.compile('rowspan\s*=\s*"\s*2\s*"')
    assert len(cl_check.findall(row1_parts[0]))>0
    assert len(row1_parts)==7
    assert len(row2_parts)==5
    #print("pass")

def test_row_span_latex():
    "This test col_span works in latex"
    t1_latex = t()._repr_latex_()
    row_split = re.compile(r'\\\\')
    lines = row_split.split(t1_latex)
    assert len(lines)==4
    col_split = re.compile('&')
    row1_parts = col_split.split(lines[0])
    row2_parts = col_split.split(lines[1])
    cl_check = re.compile('\w*\\multirow\s*\{\s*2\s*}')
    assert len(cl_check.findall(row1_parts[0]))>0
    assert row2_parts[0].strip().replace('\n','')==''
    #print("pass")

def test_row_span_format_html():
    t = Table(TableHeaderRow('A', 'B', 'C', 'D'),
              (1.50, TableCell(3.5678, row_span=2), 23, 10.9876),
              (112.679, 74.2974, 2, 7.46036),
              col_format=('{:.2g}', '{:.3g}', '{:d}', '{:10.4g}'))
    expected = (('A', 'B', 'C', 'D'),
                ('1.5', '3.57', '23', '     10.99'),
                ('1.1e+02', '2', '      7.46'))

    t_html = t._repr_html_()
    row_split = re.compile('<\s*tr\s*>')
    col_split = re.compile(r'(?<=\>).*?(?=\<)')

    for row, row_exp in zip(row_split.split(t_html)[1:], expected):
        cells = [c for c in col_split.findall(row) if c]
        for cell, cell_exp in zip(cells, row_exp):
             assert cell == cell_exp

def test_row_span_format_latex():
    t = Table(TableHeaderRow('A', 'B', 'C', 'D'),
              (1.50, TableCell(3.5678, row_span=2), 23, 10.9876),
              (112.679, 74.2974, 2, 7.46036),
              col_format=('{:.2g}', '{:.3g}', '{:d}', '{:10.4g}'))
    expected = (('A', 'B', 'C', 'D'),
                ('1.5', '3.57', '23', '     10.99'),
                ('1.1e+02', '2', '      7.46'))

    t_latex = t._repr_latex_()
    row_split = re.compile(r'\n')
    col_split = re.compile(r' & ')

    lines = row_split.split(t_latex)
    # check header
    for cell, cell_exp in zip(col_split.split(lines[2]), expected[0]):
        assert cell_exp in cell

    # check body
    for row, row_exp in zip(lines[4:-2], expected[1:]):
        cells = [c for c in col_split.split(row) if c]
        for cell, cell_exp in zip(cells, row_exp):
             assert cell_exp in cell
