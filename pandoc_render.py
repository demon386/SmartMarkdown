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
import os.path
import sys
import subprocess
from subprocess import PIPE


class PandocRenderCommand(sublime_plugin.TextCommand):
    def is_enabled(self):
        return self.view.score_selector(0, "text.html.markdown") > 0

    def is_visible(self):
        return True

    def run(self, edit, target="pdf", open_after=True, save_result=False):
        if target not in ["html", "docx", "pdf"]:
            raise Exception("Format %s currently unsopported" % target)

        self.setting = sublime.load_settings("SmartMarkdown.sublime-settings")

        encoding = self.view.encoding()
        if encoding == 'Undefined':
            encoding = 'UTF-8'
        elif encoding == 'Western (Windows 1252)':
            encoding = 'windows-1252'
        contents = self.view.substr(sublime.Region(0, self.view.size()))
        contents = contents.encode(encoding)

        file_name = self.view.file_name()
        if file_name:
            os.chdir(os.path.dirname(file_name))

        # write buffer to temporary file
        # This is useful because it means we don't need to save the buffer
        tmp_md = tempfile.NamedTemporaryFile(delete=False, suffix=".md")
        tmp_md.write(contents)
        tmp_md.close()

        # output file...
        suffix = "." + target
        if save_result:
            output_name = os.path.splitext(self.view.file_name())[0] + suffix
            if not self.view.file_name():
                raise Exception("Please safe the buffer before trying to export with pandoc.")
        else:
            output = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            output.close()
            output_name = output.name

        args = self.pandoc_args(target)
        self.run_pandoc(tmp_md.name, output_name, args)

        if open_after:
            self.open_result(output_name, target)
        #os.unlink(tmp_md.name)

    def run_pandoc(self, infile, outfile, args):
        cmd = ['pandoc'] + args
        cmd += [infile, "-o", outfile]

        # Merge the path in settings
        setting_path = self.setting.get("tex_path", [])
        for p in setting_path:
            if p not in os.environ["PATH"]:
                os.environ["PATH"] += ":" + p

        try:
            # Use the current directory as working dir whenever possible
            file_name = self.view.file_name()
            if file_name:
                working_dir = os.path.dirname(file_name)
                p = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE,
                                     cwd=working_dir)

            else:
                p = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
            p.wait()
            out, err = p.communicate()
            if err:
                raise Exception("Command: %s\n" % " ".join(cmd) + "\nErrors: " + err)
        except Exception as e:
            sublime.error_message("Fail to generate output.\n{0}".format(e))

    def pandoc_args(self, target):
        """
        Create a list of arguments for the pandoc command
        depending on the target.
        TODO: Actually do something sensible here
        """
        # Merge the args in settings
        args = self.setting.get("pandoc_args", [])

        if target == "pdf":
            args += self.setting.get("pandoc_args_pdf", [])
        if target == "html":
            args += self.setting.get("pandoc_args_html", []) + ['-t', 'html5']
        if target == "docx":
            args += self.setting.get("pandoc_args_docx", []) + ['-t', 'docx']
        return args

    def open_result(self, outfile, target):
        if target == "html":
            webbrowser.open_new_tab(outfile)
        elif sys.platform == "win32":
            os.startfile(outfile)
        elif "mac" in sys.platform or "darwin" in sys.platform:
            os.system("open %s" % outfile)
            print(outfile)
        elif "posix" in sys.platform or "linux" in sys.platform:
            os.system("xdg-open %s" % outfile)
