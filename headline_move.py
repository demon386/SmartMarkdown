"""This module provides commands for easily moving between headilnes.
"""
# Author: Muchenxuan Tong <demon386@gmail.com>

import sublime, sublime_plugin

import headline


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
                level = self._get_current_headline_level(region.a)
            else:
                level = headline.ANY_LEVEL

            if forward:
                match_region, _ = headline.find_next_headline(self.view,\
                                                           region.a,\
                                                           level,\
                                                           level_type,\
                                                           skip_headline_at_point=True,\
                                                           skip_folded=True)
                if not match_region:
                    size = self.view.size()
                    match_region = sublime.Region(size, size)
            else:
                match_region, _ = headline.find_previous_headline(self.view,\
                                                                  region.a,\
                                                                  level,\
                                                                  level_type,\
                                                                  skip_headline_at_point=True,\
                                                                  skip_folded=True)
                if not match_region:
                    match_region = sublime.Region(0, 0)
            new_sel.append(sublime.Region(match_region.a, match_region.a))

        self.view.sel().clear()
        for region in new_sel:
            self.view.sel().add(region)

    def _get_current_headline_level(self, from_point):
        """Return the current headline level of the point.

        If it's in a headline, then return the level of the headline.
        Otherwise search the headline above.
        """
        # First treat the current line as headline
        headline_content = self.view.substr(self.view.line(from_point))
        level = headline.extract_level_from_headline(headline_content)

        if not level:
            headline_region, _ = headline.find_previous_headline(self.view,\
                                                              from_point,\
                                                              headline.ANY_LEVEL,
                                                              skip_folded=True)
            headline_content = self.view.substr(self.view.line(headline_region))
            level = headline.extract_level_from_headline(headline_content)

        return level
