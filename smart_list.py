import sublime, sublime_plugin
import re

ORDER_LIST_PATTERN = re.compile(r"(\s*)(\d+)(\.\s+)\S+")
UNORDER_LIST_PATTERN = re.compile(r"(\s*[-*]+)(\s+)\S+")
EMPTY_LIST_PATTERN = re.compile(r"([-*]|\d+)(\.)*\s+$")

class SmartListCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            line_region = self.view.line(region)
            line_to_point_region = sublime.Region(line_region.a,
                                                  region.a)
            line_content = self.view.substr(line_to_point_region)
            match = ORDER_LIST_PATTERN.match(line_content)
            if match:
                insert_text = match.group(1) + \
                              str(int(match.group(2)) + 1) + \
                              match.group(3)
                self.view.insert(edit, region.a, "\n" + insert_text)
                break

            match = UNORDER_LIST_PATTERN.match(line_content)
            if match:
                insert_text = match.group(1) + match.group(2)
                self.view.insert(edit, region.a, "\n" + insert_text)
                break

            match = EMPTY_LIST_PATTERN.match(line_content)
            if match:
                self.view.sel().add(line_to_point_region)
                self.view.run_command("add_to_kill_ring", {"forward": True})
                self.view.run_command('right_delete')
                break

            self.view.insert(edit, region.a, '\n')
            self.view.show(region)
