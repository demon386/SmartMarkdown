"""Smart is inspired by the Table behavior of Org-mode.

Markdown itself doesn't support grid table, yet pandoc does.

@todo: add a key binding for converting grid table to the simple one
"""
# Author: Muchenxuan Tong <demon386@gmail.com>
# LICENSE: MIT

import sublime
import sublime_plugin

try:
    from . import table
except ValueError:
    import table


class SmartTable(sublime_plugin.TextCommand):
    def run(self, edit, forward=True):
        new_sel = []
        for r in self.view.sel():
            point = r.a

            for i in self.view.folded_regions():
                if i.contains(sublime.Region(point, point)):
                    return
            t = table.convert_table_at_point_as_list(self.view, point)
            t = table.reformat_table_list(t)
            t_str = table.convert_table_list_to_str(t)

            # Both are 0-based
            cur_row_num, cur_col_num = table.get_point_row_and_col(self.view, point)
            table_row_num = len(t)
            line_num, _ = self.view.rowcol(point)
            start_line_num = line_num - cur_row_num
            start_point = self.view.text_point(line_num - cur_row_num, 0)
            end_line_num = line_num + table_row_num - cur_row_num - 1
            end_line_start_point = self.view.text_point(end_line_num, 0)
            end_point = self.view.line(end_line_start_point).b

            # Erase the previous table region, use the new one for substitution.
            self.view.erase(edit, sublime.Region(start_point, end_point))
            self.view.insert(edit, start_point, t_str)

            if forward:
                if cur_col_num is None or cur_col_num >= len(t[0]) - 1:
                    line_num += 1
                    while(table.is_line_separator(self.view, line_num)):
                        line_num += 1
                    cur_col_num = 0
                else:
                    cur_col_num += 1
            else:
                if cur_col_num is None or cur_col_num <= 0:
                    line_num -= 1
                    while(table.is_line_separator(self.view, line_num)):
                        line_num -= 1
                    cur_col_num = len(t[0]) - 1
                else:
                    cur_col_num -= 1

            # Add a new line when at the end of the table.
            if line_num < start_line_num or line_num > end_line_num:
                col_pos = 0
                if line_num > end_line_num:
                    self.view.insert(edit, self.view.text_point(line_num, 0), "\n")
            else:
                col_pos = self.calculate_col_point(t, cur_col_num)

            new_sel.append(self.view.text_point(line_num, col_pos))

        self.view.sel().clear()
        for r in new_sel:
            self.view.sel().add(r)
            self.view.show(r)

    def calculate_col_point(self, formatted_table, col_num):
        i = 0
        while table.SEPARATOR_PATTERN.match(formatted_table[i][0]):
            i += 1

        cols_length = [len(j) for j in formatted_table[i]]
        point = 2
        for i in range(col_num):
            point += cols_length[i] + 3
        return point
