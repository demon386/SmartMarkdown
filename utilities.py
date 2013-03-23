"""Some utility functions for working with sublime.
"""


def text_at_line(view, line_num):
    """Return the content at line. None if out of boundary."""
    if line_num < 0:
        return None

    max_line_num, _ = view.rowcol(view.size())
    if line_num > max_line_num:
        return None

    point = view.text_point(line_num, 0)
    line_region = view.line(point)
    return view.substr(line_region)

def is_region_void(region):
    if region == None:
        return True
    if region.a == -1 and region.b == -1:
        return True
    return False