"""Smart folding is a feature borrowed from [Org-mode](http://org-mode.org).

It enables folding / unfolding the headlines by simply pressing TAB on headlines.

Global headline folding / unfolding is recommended to be trigged by Shift + TAB,
at anywhere.

"""
# Author: Muchenxuan Tong <demon386@gmail.com>

import re

import sublime
import sublime_plugin

try:
    from . import headline
    from .utilities import is_region_void
except ValueError:
    import headline
    from utilities import is_region_void


HEADLINE_PATTERN = re.compile(r'^(#+)\s.*')


class SmartNewLineCommand(sublime_plugin.TextCommand):
    """Changes behavior of default 'insert line after'
       Puts new line after folding mark if any.
    """
    def run(self, edit):
        points = []
        for s in self.view.sel():
            r = self.view.full_line(s)
            if headline._is_region_folded(r.b + 1, self.view):
                i = headline.region_of_content_of_headline_at_point(self.view, s.b)
            else:
                i = sublime.Region(r.a, r.b - 1)
            points.append(i)
            self.view.insert(edit, i.b, '\n')
        self.view.sel().clear()
        for p in points:
            self.view.sel().add(p.b + 1)


class SmartFoldingCommand(sublime_plugin.TextCommand):
    """Smart folding is used to fold / unfold headline at the point.

    It's designed to bind to TAB key, and if the current line is not
    a headline, a \t would be inserted.

    """
    def run(self, edit):
        ever_matched = False
        for region in self.view.sel():
            matched = self.fold_or_unfold_headline_at_point(region.a)
            if matched:
                ever_matched = True
        if not ever_matched:
            for r in self.view.sel():
                self.view.insert(edit, r.a, '\t')
                self.view.show(r)

    def fold_or_unfold_headline_at_point(self, from_point):
        """Smart folding of the current headline.

        Unfold only when it's totally folded. Otherwise fold it.

        """
        _, level = headline.headline_and_level_at_point(self.view,
                                                        from_point)
        # Not a headline, cancel
        if level is None or not headline.is_scope_headline(self.view, from_point):
            return False

        content_region = headline.region_of_content_of_headline_at_point(self.view,
                                                                         from_point)
        # If the content is empty, Nothing needs to be done.
        if content_region is None:
            # Return True because there is a headline anyway.
            return True

        # Check if content region is folded to decide the action.
        if self.is_region_totally_folded(content_region):
            self.unfold_yet_fold_subheads(content_region, level)
        else:
            self.view.fold(sublime.Region(content_region.a - 1, content_region.b))
        return True

    def is_region_totally_folded(self, region):
        """Decide if the region is folded. Treat empty region as folded."""
        if (region is None) or (region.a == region.b):
            return True

        for i in self.view.folded_regions():
            if i.contains(region):
                return True
        return False

    def unfold_yet_fold_subheads(self, region, level):
        """Unfold the region while keeping the subheadlines folded."""
        ## First unfold all
        self.view.unfold(region)
        ## Fold subheads
        child_headline_region, _ = headline.find_headline(self.view, region.a, level, True, \
                                                          headline.MATCH_CHILD)

        while (not is_region_void(child_headline_region) and child_headline_region.b <= region.b):
            child_content_region = headline.region_of_content_of_headline_at_point(self.view,
                                                                                   child_headline_region.a)
            if child_content_region is not None:
                self.view.fold(sublime.Region(child_content_region.a - 1, child_content_region.b))
                search_start_point = child_content_region.b
            else:
                search_start_point = child_headline_region.b

            child_headline_region, _ = headline.find_headline(self.view, \
                                                              search_start_point, level, True, \
                                                              headline.MATCH_CHILD,
                                                              skip_headline_at_point=True)


class GlobalFoldingCommand(SmartFoldingCommand):
    """Global folding / unfolding headlines at any point.

    Unfold only when top-level headlines are totally folded.
    Otherwise fold.

    """
    def run(self, edit):
        if self.is_global_folded():
            # Unfold all
            self.unfold_all()
        else:
            self.fold_all()

    def is_global_folded(self):
        """Check if all headlines are folded.
        """
        region, level = headline.find_headline(self.view, 0, \
                                               headline.ANY_LEVEL, True)
        # Treating no heeadline as folded, since unfolded all makes
        # no harm in this situation.
        if is_region_void(region):
            return True

        point = region.a
        # point can be zero
        while (point is not None and region):
            region = headline.region_of_content_of_headline_at_point(self.view, \
                                                                     point)
            if not is_region_void(region):
                point = region.b
            if not self.is_region_totally_folded(region):
                return False
            else:
                region, level = headline.find_headline(self.view, point, \
                                                       headline.ANY_LEVEL, \
                                                       True,
                                                       skip_headline_at_point=True)
                if not is_region_void(region):
                    point = region.a
        return True

    def unfold_all(self):
        self.view.unfold(sublime.Region(0, self.view.size()))
        self.view.show(self.view.sel()[0])

    def fold_all(self):
        region, level = headline.find_headline(self.view, \
                                               0, \
                                               headline.ANY_LEVEL, \
                                               True)

        # At this point, headline region is sure to exist, otherwise it would be
        # treated as gobal folded. (self.is_global_folded() would return True)
        point = region.a
        # point can be zero
        while (point is not None and region):
            region = headline.region_of_content_of_headline_at_point(self.view, \
                                                                     point)
            if not is_region_void(region):
                point = region.b
                self.view.fold(sublime.Region(region.a - 1, region.b))
            region, level = headline.find_headline(self.view, point, \
                                                   headline.ANY_LEVEL,
                                                   True, \
                                                   skip_headline_at_point=True)
            if not is_region_void(region):
                point = region.a
        self.adjust_cursors_and_view()

    def adjust_cursors_and_view(self):
        """After folder, adjust cursors and view.

        If the current point is inside the folded region, move it move
        otherwise it's easy to perform some unintentional editing.

        """
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
