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
            matched = self.fold_or_unfold_headline_at_point(region.a, headline.ANY_LEVEL)
            if matched:
                ever_matched = True
        if not ever_matched:
            for r in self.view.sel():
                self.view.insert(edit, r.a, '\t')
                self.view.show(r)

    def fold_or_unfold_headline_at_point(self, from_point, level):
        """Smart folding of the current headline.

        Unfold only when it's totally folded. Otherwise fold it.

        """
        _, level = headline.headline_and_level_at_point(self.view,
                                                        from_point)
        # Not a headline, cancel
        if level is None:
            return False

        content_region = headline.region_of_content_of_headline_at_point(self.view,
                                                                         from_point)
        # If the content is empty, Nothing needs to be done.
        if content_region is None:
            return True

        # Check if content region is folded to decide the action.
        if self._is_region_totally_folded(content_region):
            self._unfold_yet_fold_subheads(content_region, level)
        else:
            self.view.fold(content_region)
        return True

    def _is_region_totally_folded(self, region):
        if (region is None) or (region.a == region.b):
            return True

        for i in self.view.folded_regions():
            if i.contains(region):
                return True
        return False

    def _unfold_yet_fold_subheads(self, region, level):
        "Keep the subheadlines folded."
        self.view.unfold(region)
        ## fold subheads
        start_line, _ = self.view.rowcol(region.a)
        end_line, _ = self.view.rowcol(region.b)

        for i in range(start_line, end_line + 1):
            region = self.view.text_point(i, 0)
            self.fold_or_unfold_headline_at_point(region, level + 1)


class GlobalFoldingCommand(SmartFoldingCommand):
    """Global folding / unfolding headlines at any point.

    Unfold only when top-level headlines are totally folded.
    Otherwise fold.
    """
    def run(self, edit):
        if self._is_global_folded():
            # Unfold all
            self._unfold_all()
        else:
            self._fold_all()

    def _is_global_folded(self):
        """Check if all headlines are folded"""
        region, level = headline.find_next_headline(self.view,\
                                                    0,\
                                                    headline.ANY_LEVEL)
        # Treating no heeadline as folded, since unfolded all makes no harm
        if not region:
            return True

        point = region.a
        # point can be zero
        while (point is not None and region):
            region = headline.region_of_content_of_headline_at_point(self.view,\
                                                                     point)
            if region:
                point = region.b
            if not self._is_region_totally_folded(region):
                return False
            else:
                region, level = headline.find_next_headline(self.view, point,\
                                                            headline.ANY_LEVEL,
                                                            skip_headline_at_point=True)
                if region:
                    point = region.a
        return True

    def _unfold_all(self):
        self.view.unfold(sublime.Region(0, self.view.size()))
        self.view.show(self.view.sel()[0])

    def _fold_all(self):
        region, level = headline.find_next_headline(self.view,\
                                                    0,\
                                                    headline.ANY_LEVEL)

        # At this point, headline region is sure to exist, otherwise it would be
        # treated as gobal folded. (self._is_global_folded() would return True)
        point = region.a
        # point can be zero
        while (point is not None and region):
            region = headline.region_of_content_of_headline_at_point(self.view,\
                                                                     point)
            if region:
                point = region.b
                self.view.fold(region)
            region, level = headline.find_next_headline(self.view, point,\
                                                        headline.ANY_LEVEL,
                                                        skip_headline_at_point=True)
            if region:
                point = region.a
        self._adjust_cursors_and_view()

    def _adjust_cursors_and_view(self):
        # If the current point is inside the folded region, move it move
        # otherwise it's easy to perform some unintentional editing.
        folded_regions = self.view.folded_regions()
        new_sel = []

        for r in self.view.sel():
            for folded in folded_regions:
                if folded.contains(r):
                    new_sel.append(sublime.Region(folded.b, folded.b))
                    break
            else:
                new_sel.append(r)

        self.view.sel().clear()
        for r in new_sel:
            self.view.sel().add(r)
            self.view.show(r)