import sublime, sublime_plugin
import re

HEADLINE_PATTERN = re.compile(r'^(#+)\s.*')


class SmartFoldingCommand(sublime_plugin.TextCommand):
    def region_before_next_headline_or_eof(self, content_line_start_point, level):
        next_headline = self.view.find(r'^#{1,%d}\s.*' % level,
                                       content_line_start_point)
        if next_headline != None:
            end_pos = next_headline.a - 1
        else:
            end_pos = self.view.size()
        return sublime.Region(content_line_start_point, end_pos)

    def is_totally_folded(self, region):
        for i in self.view.folded_regions():
            if i == region:
                return True
        return False

    def unfold_yet_fold_subheads(self, region, level):
        "Keep the subheadlines folded."
        self.view.unfold(region)
        ## fold subheads
        start_line, _ = self.view.rowcol(region.a)
        end_line, _ = self.view.rowcol(region.b)

        for i in range(start_line, end_line + 1):
            self.fold_or_unfold_headline(i, level + 1)

    def fold_or_unfold_headline(self, line_num, level):
        line_region = self.view.line(self.view.text_point(line_num, 0))
        line_content = self.view.substr(line_region)
        # We need next line to check this is an empty headline
        next_line_region = self.view.line(self.view.text_point(line_num + 1, 0))
        next_line_content = self.view.substr(next_line_region)

        if level == -1:
            # Any level
            match = HEADLINE_PATTERN.match(line_content)
            if match:
                level = len(match.group(1))

        pattern = re.compile(r'^(#{1,%d})\s.*' % level)
        match = pattern.match(line_content)
        next_line_match = pattern.match(next_line_content)

        if next_line_match:
            return True

        if match:
            content_line_start_point = self.view.text_point(line_num + 1, 0)
            content_region = self.region_before_next_headline_or_eof(content_line_start_point,
                                                                     level)
            if self.is_totally_folded(content_region):
                self.unfold_yet_fold_subheads(content_region, level)
            else:
                self.view.fold(content_region)
            return True
        else:
            return False

    def run(self, edit):
        ever_matched = False
        for region in self.view.sel():
            # Extract the line content
            line_num, _ = self.view.rowcol(region.a)
            matched = self.fold_or_unfold_headline(line_num, -1)
            if matched:
                ever_matched = True
        if not ever_matched:
            for i in self.view.sel():
                self.view.insert(edit, i.a, '\t')
