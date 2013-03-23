"""Utilities function for working with grid table of Pandoc

Terminologies

- Table list :: This is not a list of tables, but rather converting the table as
a nested python list. Each row is a sub-list in the table list.

"""
# Author: Muchenxuan Tong <demon386@gmail.com>
# LICENSE: MIT

import re
import copy

import sublime

try:
    from . import utilities
except ValueError:
    import utilities

TABLE_PATTERN = re.compile(r"\s*\|")
SEPARATOR_PATTERN = re.compile(r"\s*(\+[=-])")


def convert_table_at_point_as_list(view, from_point):
    """Get the table at the point.
    Transform the table to python list.

    Returns
    -------
    table: list
        A nested list representing the table.
    indent: "str" (@todo not impelmented yet)
        String of indentation, used in every row.

    """
    table_above = convert_table_above_or_below_as_list(view, from_point, above=True)
    table_below = convert_table_above_or_below_as_list(view, from_point, above=False)
    row_at_point = convert_row_at_point_as_list(view, from_point)

    table = table_above + [row_at_point] + table_below
    return table


def convert_table_above_or_below_as_list(view, from_point, above):
    """Convert the table above the point as python list.

    Returns
    -------
    table: list
        A nested list representing the table.

    """
    line_num, _ = view.rowcol(from_point)
    line_num += - 1 if above else 1

    line_text = utilities.text_at_line(view, line_num)
    table = []

    while line_text and (TABLE_PATTERN.match(line_text) or
                         SEPARATOR_PATTERN.match(line_text)):
        table.append(_convert_row_text_as_list(line_text))
        line_num += -1 if above else 1
        line_text = utilities.text_at_line(view, line_num)

    if above:
        table = table[::-1]

    return table


def convert_row_at_point_as_list(view, from_point):
    """Convert the row at point as a python list.
    """
    line_num, _ = view.rowcol(from_point)
    line_text = utilities.text_at_line(view, line_num)

    return _convert_row_text_as_list(line_text)


def _convert_row_text_as_list(row_text):
    """Convert the text of a row into a python list.

    Paramters
    ---------
    row_text: str
        The text of the row.

    Returns
    -------
    lst: list
        The converted list.

    """
    split_row = row_text.split("|")

    if len(split_row) > 2 and split_row[-1].strip() == "":
        lst = split_row[1:-1]
    else:
        lst = split_row[1:]

    match = SEPARATOR_PATTERN.match(row_text)
    if match:
        lst = [match.group(1)]

    return [i.strip() for i in lst]


def reformat_table_list(table):
    """Reformat & align the table list.

    After this, every column is of the same length,
    and every row is of the same number of column.

    """
    cols_num = max([len(row) for row in table])
    cols_length = _get_cols_length(table, cols_num)

    new_table = []
    for row in table:
        new_row = []
        if not SEPARATOR_PATTERN.match(row[0]):
            for i in range(cols_num):
                try:
                    col = row[i]
                    new_row.append(col + " " * (cols_length[i] - len(col)))
                except:
                    new_row.append(" " * cols_length[i])
        else:
            marker = row[0][1]
            for i in range(cols_num):
                new_row.append(marker * (cols_length[i] + 2))
            # Add a mark for recognization
            new_row[0] = "+" + new_row[0]
        new_table.append(new_row)
    return new_table


def convert_table_list_to_str(table):
    """Convert the python list to str for outputing.

    """
    table_str = ""
    table = copy.deepcopy(table)
    for row in table:
        if SEPARATOR_PATTERN.match(row[0]):
            row[0] = row[0][1:]  # Remove the mark added in reformat_table_list
            row_str = "+"
            for col_str in row:
                row_str += col_str + "+"
        else:
            row_str = "|"
            for col_str in row:
                row_str += " " + col_str + " " + "|"
        table_str += row_str + "\n"
    return table_str[:-1]


def _get_cols_length(table, cols_num):
    """Return the max length of every columns.
    """
    cols_length = [0] * cols_num
    for row in table:
        for (i, col) in enumerate(row):
            col_len = len(col)
            if col_len > cols_length[i]:
                cols_length[i] = col_len
    return cols_length


def get_point_row_and_col(view, from_point):
    """Return the row and col the current point is in the table.
    """
    line_num, _ = view.rowcol(from_point)
    line_num -= 1

    line_text = utilities.text_at_line(view, line_num)
    row_num = 0
    while line_text and (TABLE_PATTERN.match(line_text) or
                         SEPARATOR_PATTERN.match(line_text)):
        row_num += 1
        line_num -= 1
        line_text = utilities.text_at_line(view, line_num)

    line_start_point = view.line(from_point)
    region = sublime.Region(line_start_point.a, from_point)
    precedding_text = view.substr(region)

    split_row = precedding_text.split("|")
    if len(split_row) >= 2:
        col_num = len(split_row) - 2
    elif split_row[0].strip() == "":
        col_num = -1
    else:
        col_num = None
    return (row_num, col_num)


def is_line_separator(view, line_num):
    """Check if the current line is a separator.
    """
    text = utilities.text_at_line(view, line_num)
    if text and SEPARATOR_PATTERN.match(text):
        return True
    else:
        return False
