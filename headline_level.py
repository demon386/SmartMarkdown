"""This file is contributed by [David Smith](https://github.com/djs070)
"""
import sublime
import sublime_plugin


class ChangeHeadingLevelCommand(sublime_plugin.TextCommand):
    def run(self, edit, up=True):
        for region in self.view.sel():
            line = self.view.line(region)
            if up:
                # Increase heading level
                if not self.view.substr(line)[0] in ['#', ' ']:
                    self.view.insert(edit, line.begin(), " ")
                self.view.insert(edit, line.begin(), "#")
            else:
                # Decrease heading level
                if self.view.substr(line)[0] == '#':
                    self.view.erase(edit, sublime.Region(line.begin(), line.begin() + 1))
                    if self.view.substr(line)[0] == ' ':
                        self.view.erase(edit, sublime.Region(line.begin(), line.begin() + 1))
