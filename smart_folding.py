"""Smart folding is a feature borrowed from [Org-mode](http://org-mode.org).

It enables folding / unfolding the headlines by simply pressing TAB on headlines.

Global headline folding / unfolding is recommended to be trigged by Shift + TAB,
at anywhere.
"""
# Author: Muchenxuan Tong <demon386@gmail.com>

import re

import sublime
import sublime_plugin

import headline


HEADLINE_PATTERN = re.compile(r'^(#+)\s.*')


class SmartFoldingCommand(sublime_plugin.TextCommand):
    """Smart folding is used to fold / unfold headline at the point.

    It's designed to bind to TAB key, and if the current line is not
    a headline, a \t would be inserted.
    """
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
        content_region = self._region_before_next_parent_headline_or_eof(content_line_start_point,
                                                                        level)

        if self._is_region_totally_folded(content_region):
            self._unfold_yet_fold_subheads(content_region, level)
        else:
            self.view.fold(content_region)
        return True

    def _region_before_next_parent_headline_or_eof(self, content_line_start_point, level):
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

    def _is_region_totally_folded(self, region):
        for i in self.view.folded_regions():
            if i == region:
                return True
        return False

    def _unfold_yet_fold_subheads(self, region, level):
        "Keep the subheadlines folded."
        self.view.unfold(region)
        ## fold subheads
        start_line, _ = self.view.rowcol(region.a)
        end_line, _ = self.view.rowcol(region.b)

        for i in range(start_line, end_line + 1):
            self.fold_or_unfold_headline_at_line(i, level + 1)


class GlobalFoldingCommand(SmartFoldingCommand):
    """Global folding / unfolding headlines at any point.

    Unfold only when top-level headlines are totally folded.
    Otherwise fold.
    """
    def run(self, edit):
        if self._is_global_folded():
            # Unfold all
            self.view.unfold(sublime.Region(0, self.view.size()))
            self.view.show(self.view.sel()[0])
        else:
            # Fold all
            region, level = headline.find_next_headline(self.view,\
                                                        0,\
                                                        headline.ANY_LEVEL)
            # Headline region must be exists, otherwise it would be treated
            # as gobal folded.
            point = self._point_of_beginning_of_next_line(region.a)

            while(point and region):
                region = self._region_before_next_parent_headline_or_eof(point,\
                                                                        level)
                self.view.fold(region)
                region, level = headline.find_next_headline(self.view, region.b,\
                                                            headline.ANY_LEVEL,
                                                            skip_headline_at_point=True)
                if region:
                    point = self._point_of_beginning_of_next_line(region.a)

            # If the current point is inside the folded region, move it move
            # otherwise it's easy to perform some unintentional editing.
            folded_regions = self.view.folded_regions()
            new_sel = []
            for r in self.view.sel():
                for folded in folded_regions:
                    if folded.contains(r):
                        new_sel.append(folded.b)
                        break
                else:
                    new_sel.append(r)
            self.view.sel().clear()
            for r in new_sel:
                self.view.sel().add(r)
                self.view.show(r)

    def _is_global_folded(self):
        """Check if all headlines are folded"""
        region, level = headline.find_next_headline(self.view,\
                                                        0,\
                                                        headline.ANY_LEVEL)
        # Treating no heeadline as folded, since unfolded all makes no harm
        if not region:
            return True

        point = self._point_of_beginning_of_next_line(region.a)
        while(point and region):
            region = self._region_before_next_parent_headline_or_eof(point,\
                                                                    level)
            if not self._is_region_totally_folded(region):
                return False
            else:
                region, level = headline.find_next_headline(self.view, region.b,\
                                                            headline.ANY_LEVEL,
                                                            skip_headline_at_point=True)
                if region:
                    point = self._point_of_beginning_of_next_line(region.a)
        return True

    def _point_of_beginning_of_next_line(self, from_point):
        "Return the point of the beginning of next line. None if EOF."
        line_num, _ = self.view.rowcol(from_point)
        point = self.view.text_point(line_num + 1, 0)
        if point >= self.view.size():
            return None
        else:
            return point
