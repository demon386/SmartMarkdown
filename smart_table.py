"""Smart is inspired by the Table behavior of Org-mode.

Markdown itself doesn't support grid table, yet pandoc does.

@todo: add a key binding for converting grid table to the simple one
"""

import sublime
import sublime_plugin

import table


class SmartTable(sublime_plugin.TextCommand):
    def run(self, edit, forward=True):
        new_sel = []

        point = self.view.sel()[0].a
        # Both are 0-based
        t = table.convert_table_at_point_as_list(self.view, point)
        print(t)
        t = table.reformat_table_list(t)
        t_str = table.convert_table_list_to_str(t)
        print(t_str)

        cur_row_num, cur_col_num = table.get_point_row_and_col(self.view, point)
        table_row_num = len(t)
        line_num, _ = self.view.rowcol(point)
        start_point = self.view.text_point(line_num - cur_row_num, 0)
        end_line_start = self.view.text_point(line_num + table_row_num - cur_row_num - 1, 0)
        end_point = self.view.line(end_line_start).b

        self.view.erase(edit, sublime.Region(start_point, end_point))
        self.view.insert(edit, start_point, t_str)

        print(cur_col_num)
        print(len(t[0]))
        if forward:
            if cur_col_num is None or cur_col_num >= len(t[0]) - 1:
                line_num += 1
                while(table.is_line_separator(self.view, line_num)):
                    line_num += 1
                cur_col_num = 0
            else:
                cur_col_num += 1
        else:
            if cur_col_num is None or cur_col_num == 0:
                line_num -= 1
                while(table.is_line_separator(self.view, line_num)):
                    line_num -= 1
                cur_col_num = len(t[0]) - 1
            else:
                cur_col_num -= 1


        col_pos = self.calculate_col_point(t, cur_col_num)
        new_sel.append(self.view.text_point(line_num, col_pos))

        self.view.sel().clear()
        self.view.sel().add(new_sel[0])

    def calculate_col_point(self, formatted_table, col_num):
        cols_length = [len(i) for i in formatted_table[0]]
        point = 2
        for i in range(col_num):
            point += cols_length[i] + 1
        return point

