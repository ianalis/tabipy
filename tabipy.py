#name: tabipy.py
#type: text/x-python
#size: 8195 bytes 
#---- 
import re
import sys
PY3 = sys.version_info[0] >= 3

try:
    from itertools import zip_longest  # Python 3
except ImportError:
    from itertools import izip_longest as zip_longest  # Python 2
from collections import Mapping

class TableCell(object):
    bg_colour = None
    _latex_escape_table = {'&': r'\&',
                           '\\': r'{\textbackslash}',
                           '~': r'{\textasciitilde}',
                           '$': '\$',
                           '\r\n': r'{\linebreak}',
                           '\n': r'{\linebreak}',
                           '\r': r'{\linebreak}',
                           '_': r'\_',
                           '{': '\{',
                           '}': '\}'}
    _latex_escape_re = None
    
    def __init__(self, value, header=False, bg_colour=None, text_colour=None,
                 col_span=1, format=None):
        self.value = value
        self.header = header
        self.bg_colour = bg_colour
        self.text_colour = text_colour
        self.col_span = col_span
        self.format = format

        # initialize regex for escaping to latex code
        if self._latex_escape_re is None:
            self._latex_escape_re = re.compile('|'.join(map(re.escape, 
                                        sorted(self._latex_escape_table.keys(),
                                               key=len, reverse=True))))

    def _latex_escape_func(self, match): 
        """Replace regex match with latex equivalent"""
        return self._latex_escape_table[match.group()]
    
    def _make_css(self):
        rules = []
        if self.bg_colour:
            rules.append('background-color:%s' % self.bg_colour)
        if self.text_colour:
            rules.append('color:%s' % self.text_colour)
        return '; '.join(rules)
        
    def _check_span(self,val):
        "Validate the span value."
        val = int(val)
        if val<1:
            er = "Row and columns spand must be greater or equal to 1"
            raise(ValueError(er))
        return val
    
    @property
    def col_span(self):
        return self._col_span
    @col_span.setter
    def col_span(self,val):
        val = self._check_span(val)
        self._col_span = val

    def formatted_value(self):
        return (self.format.format if self.format else u'{}'.format)(self.value)
    
    def _repr_html_(self, format=None):
        tag = 'th' if self.header else 'td'
        spans = ''
        if self.col_span>1:
            spans += 'colspan="%s" '%self.col_span
        attrs = []
        style = self._make_css()
        if style:
            attrs.append('style="%s"'%style)

        if self.format:
            val = self.format.format(self.value)
        elif not self.header and format:
            # do not apply column format to headers
            val = format.format(self.value)
        else:
            val = u'{}'.format(self.value)

        return "<%s %s %s>%s</%s>"% (tag, spans,' '.join(attrs), val, tag) 

    def _repr_latex_(self):
        out = self._latex_escape_re.sub(self._latex_escape_func, 
                                        self.formatted_value())
        # the bolf flag must only be next to the value of the cell not outside
        # of the multicolumn flag
        out = u"\\bf " + out if self.header else out
        if self.col_span>1:
            text = "\multicolumn{%d}{l}{%s}"%(self.col_span, out)
        else:
            text = out
        return text

class TableHeader(TableCell):
    def __init__(self, value, **kwargs):
       # header of a TableHeader is always True
       if 'header' in kwargs:
           del kwargs['header']
       super(TableHeader, self).__init__(value, header=True, **kwargs)

class TableRow(object):
    def  __init__(self, *cells, **kwargs):
        self.max_len = kwargs.get("max_len",None)
        self.cells = []

        self.row_format = kwargs.get('format', None)
        if self.row_format:
            # check that format length is equal to number of columns
           if self.max_len and len(self.row_format) != self.max_len:
               raise ValueError('Wrong number of format strings')

        for c in cells:
            self.append_cell(c)

        if self.max_len is not None:
            cur_len = self.column_count()
            if cur_len < self.max_len:
                for c in range(self.max_len - cur_len):
                    self.append_cell('')
            
    @property
    def _current(self):
        "This provides column information for the current row"
        count = 0
        current = []
        for index, c in enumerate(self.cells):
            if index == count:
                for col in range(c.col_span):
                    cs = c.col_span
                    current.append(cs)
                    count +=1
        return current

    def set_parent(self, parent):
        self.parent = parent
            
    def append_cell(self, c):
        if not isinstance(c, TableCell):
            c = TableCell(c)
        if c.col_span>1:
            self.cells.append(c)
            index = self.column_count()
            blanks = c.col_span -1
            if self.max_len is not None:
                m_l = self.max_len
                new_len = index + blanks
                count = m_l - index if new_len > self.max_len else blanks
            else:
                count = blanks
            for blank in range(count):
                self.cells.append(TableCell(''))
        else:
            self.cells.append(c)

    def column_count(self, debug=False):
        count = 0
        for index, c in enumerate(self.cells):
            if debug:
                print('index = {}, value = "{}", col_span = {}'.format(index,
                                                                     c.value,
                                                                     c.col_span))
            if index == count:
                count += c.col_span
        return count
    
    def _repr_html_(self):
        # Note: Because of how a row is rendered, if a cell to the right of a
        # cell, with col_span greater than 1, contains content, that content 
        # will not be rendeded.  The content is not distroyed, just not rended.
        cur = self._current # Updates the current cells row span info
        html = '<tr>'
        index = 0      
        for count, c_col in enumerate(cur):
            if index == count:
                cell_format = None
                # format priority:
                # 1. cell format
                # 2. row format
                # 3. table header row format
                if self.row_format:
                    cell_format = self.row_format[index]
                elif self.parent.col_format:
                    cell_format = self.parent.col_format[index]
                html += self.cells[index]._repr_html_(cell_format)
                index += c_col
        html +='</tr>'
        return html


    def _repr_latex_(self):
        # Note: Because of how a row is rendered, if a cell to the right of a
        # cell, with col_span greater than 1, contains content, that content 
        # will not be rendeded.  The content is not distroyed, just not rended.
        cur = self._current # Updates the current cells row span info
        latex = ''
        index = 0
        for count, c_col in enumerate(cur):
            if index == count:
                _cell = self.cells[index]
                latex += _cell._repr_latex_() + ' & '
                index += c_col
        latex = latex.strip('& ')
        latex += '\\\\\n'
        return latex

class TableHeaderRow(TableRow):
    def __init__(self, *cells, **kwargs):
        self.col_format = kwargs.get('col_format')
        super(TableHeaderRow, self).__init__(*cells, **kwargs)

        # assign a row format if undefined to prevent the table column format
        # from being used
        if self.row_format is None:
            self.row_format = [u'{}'] * len(self.cells)

    def append_cell(self, c, format='{}'):
        if not isinstance(c, TableCell):
            c = TableCell(c, header=True, format=format)
        self.cells.append(c)

    def set_parent(self, parent):
        super(TableHeaderRow, self).set_parent(parent)
        self.parent.has_header = True
        self.parent.col_format = self.col_format

    def _repr_latex_(self):
        return super(TableHeaderRow, self)._repr_latex_() + '\\hline\n'

class Table(object):
    def __init__(self, *rows):
        self.rows = []
        self.has_header = False
        self.col_format = None

        # if argument is a single dict, convert it to a table with keys
        # as header
        if (len(rows) == 1) and isinstance(rows[0], Mapping):
            dict_arg = rows[0]
            new_rows = [TableHeaderRow(*dict_arg.keys())]
            new_rows.extend(zip_longest(*dict_arg.values(), fillvalue=''))
            rows = new_rows
        max_len = None
        for index, r in enumerate(rows):
#             print(max_len)
            self.append_row(r, max_len)
            if index==0:
                max_len = self.rows[0].column_count()
            
    
    def append_row(self, r, max_len=None):
        if not isinstance(r, TableRow):
            # check if a column format was assigned to table
            if self.col_format is not None:
                r = TableRow(*r, max_len=max_len, parent=self, 
                             format=self.col_format)
            else:
                r = TableRow(*r, max_len=max_len, parent=self)
        r.set_parent(self)
        self.rows.append(r)
    
    def _repr_html_(self):
        return '<table>\n' + '\n'.join(r._repr_html_() for r in self.rows) + '\n</table>'

    def _repr_latex_(self):
        out = '\n'.join(r._repr_latex_() for r in self.rows)
        if self.has_header:
            out = '\\hline\n' + out + '\\hline\n'
        return '\\begin{tabular}{*{%d}{l}}\n%s\\end{tabular}' % \
                        (self.rows[0].column_count(), out)
