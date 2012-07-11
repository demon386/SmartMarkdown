"""This file is initially forked from
[SublimePandoc](https://github.com/jclement/SublimePandoc)
by [DanielMe](https://github.com/DanielMe/)

@todo naming convention should be foo_bar rather than fooBar.
@bug PDF export doesn't work in my Mac, gonna check it later.

2012-07-02: Muchenxuan Tong changed some stylical errors (with SublimeLinter)
"""

import sublime
import sublime_plugin
import webbrowser
import tempfile
import os
import sys
import subprocess


class PandocRenderCommand(sublime_plugin.TextCommand):
    def is_enabled(self):
        return self.view.score_selector(0, "text.html.markdown") > 0

    def is_visible(self):
        return True

    def run(self, edit, target="pdf", open_after=True, save_result=False):
        if target not in ["html", "docx", "pdf"]:
            raise Exception("Format %s currently unsopported" % target)

        encoding = self.view.encoding()
        if encoding == 'Undefined':
            encoding = 'UTF-8'
        elif encoding == 'Western (Windows 1252)':
            encoding = 'windows-1252'
        contents = self.view.substr(sublime.Region(0, self.view.size()))
        contents = contents.encode(encoding)

        # write buffer to temporary file
        # This is useful because it means we don't need to save the buffer
        tmp_md = tempfile.NamedTemporaryFile(delete=False, suffix=".md")
        tmp_md.write(contents)
        tmp_md.close()

        # output file...
        suffix = "." + target
        if saveResult:
            output_name = os.path.splitext(self.view.file_name())[0] + suffix
            if not self.view.file_name():
                raise Exception("Please safe the buffer before trying to export with pandoc.")
        else:
            output = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            output.close()
            output_name = output.name

        args = self.pandoc_args(target)
        self.run_pandoc(tmp_md.name, output_name, args)

        os.unlink(tmp_md.name)
        if openAfter:
            self.open_result(output_name, target)

    def run_pandoc(self, infile, outfile, args):
        cmd = ['pandoc'] + args
        cmd += [infile, "-o", outfile]
        try:
            subprocess.call(cmd)
        except Exception as e:
            sublime.error_message("Unable to execute Pandoc.  \n\nDetails: {0}".format(e))

    def pandoc_args(self, target):
        """
        Create a list of arguments for the pandoc command
        depending on the target.
        TODO: Actually do something sensible here
        """
        if target == "pdf":
            return []
        if target == "html":
            return ['-t', 'html5']
        if target == "docx":
            return ['-t', 'docx']

    def open_result(self, outfile, target):
        if target == "html":
            webbrowser.open_new_tab(outfile)
        elif sys.platform == "win32":
            os.startfile(outfile)
        elif sys.platform == "mac":
            subprocess.call(["open", outfile])
        elif "posix" in sys.platform or "linux" in sys.platform:
            subprocess.call(["xdg-open", outfile])
