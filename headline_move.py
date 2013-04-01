"""This module provides commands for easily moving between headilnes.

The feature is borrowed from [Org-mode](http://org-mode.org).

"""
# Author: Muchenxuan Tong <demon386@gmail.com>

import sublime
import sublime_plugin

try:
    from . import headline
    from .utilities import is_region_void
except ValueError:
    import headline
    from utilities import is_region_void


class HeadlineMoveCommand(sublime_plugin.TextCommand):
    def run(self, edit, forward=True, same_level=True):
        """Move between headlines, forward or backward.

        If same_level is true, only move to headline with the same level
        or higher level.

        """
        new_sel = []
        if same_level:
            level_type = headline.MATCH_PARENT
        else:
            level_type = headline.MATCH_ANY

        for region in self.view.sel():
            if same_level:
                _, level = headline.headline_and_level_at_point(self.view,\
                                                                region.a,
                                                                search_above_and_down=True)
                if level is None:
                    return
            else:
                level = headline.ANY_LEVEL

            match_region, _ = headline.find_headline(self.view, \
                                                     region.a, \
                                                     level, \
                                                     forward, \
                                                     level_type, \
                                                     skip_headline_at_point=True,\
                                                     skip_folded=True)

            if is_region_void(match_region):
                return
            new_sel.append(sublime.Region(match_region.a, match_region.a))

        self.adjust_view(new_sel)

    def adjust_view(self, new_sel):
        self.view.sel().clear()
        for region in new_sel:
            self.view.sel().add(region)
            self.view.show(region)
