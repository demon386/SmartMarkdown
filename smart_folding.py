"""Smart folding is a feature borrowed from [Org-mode](http://org-mode.org).

It enables folding / unfolding the headlines by simply pressing TAB on headlines
"""
# Author: Muchenxuan Tong <demon386@gmail.com>

import re

import sublime
import sublime_plugin

import headline


HEADLINE_PATTERN = re.compile(r'^(#+)\s.*')


class SmartFoldingCommand(sublime_plugin.TextCommand):
    def region_before_next_parent_headline_or_eof(self, content_line_start_point, level):
        """Used to extract region of the folded headline."""
        next_headline, _ = headline.find_next_headline(self.view,
                                                       content_line_start_point,
                                                       level,
                                                       headline.MATCH_PARENT)
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
            self.fold_or_unfold_headline_at_line(i, level + 1)

    def fold_or_unfold_headline_at_line(self, line_num, level):
        """Smart folding of the current headline.

        Unfold only when it's totally folded. Otherwise fold it.

        """
        line_region = self.view.line(self.view.text_point(line_num, 0))
        line_content = self.view.substr(line_region)
        # Update the level in case it's headline.ANY_LEVEL
        level = headline.extract_level_from_headline(line_content)

        # Not a headline, cancel
        if level == None:
            return False

        # We need next line to check this is an empty headline.
        # If so, Nothing needs to be done.
        next_line_region = self.view.line(self.view.text_point(line_num + 1, 0))
        next_line_content = self.view.substr(next_line_region)
        next_line_level = headline.extract_level_from_headline(next_line_content)

        if next_line_level and next_line_level <= level:
            # Return True otherwise a '\t' would be insert
            return True

        content_line_start_point = self.view.text_point(line_num + 1, 0)
        content_region = self.region_before_next_parent_headline_or_eof(content_line_start_point,
                                                                        level)

        if self.is_totally_folded(content_region):
            self.unfold_yet_fold_subheads(content_region, level)
        else:
            self.view.fold(content_region)
        return True

    def run(self, edit):
        ever_matched = False
        for region in self.view.sel():
            # Extract the line content
            line_num, _ = self.view.rowcol(region.a)
            matched = self.fold_or_unfold_headline_at_line(line_num, headline.ANY_LEVEL)
            if matched:
                ever_matched = True
        if not ever_matched:
            for i in self.view.sel():
                self.view.insert(edit, i.a, '\t')
