# SmartMarkdown for Sublime Text 2 & 3

Author: Muchenxuan Tong (demon386@gmail.com)

## Introduction
The plugin is aimed at making editing Markdown in Sublime Text 2 easier and more powerful. Ideally, I hope we can bring several amazing features of [Org-mode](http://org-mode.org) of Emacs into Sublime Text.

## What's new
### v0.3: Adjust the position of folding mark to the end of headline. (added by [vovkkk](https://github.com/vovkkk) and [alehandrof](https://github.com/alehandrof))
### v0.2: Support for Sublime Text 3 (added by [UNOwen](https://github.com/UNOwen).)
### v0.1.6: Add support and bindings for headline level changing. (added by [David Smith](https://github.com/djs070).) The key bindings are: **Super+Shift+,** for decreasing and **Super+Shift+.** for increasing.
### v0.1.5: Basic smart table (grid table) support added. Basic Pandoc intergration (added by [DanielMe](https://github.com/DanielMe/).)
### v0.1.3: Add support for global headling folding / unfolding.
### v0.1.2: Move between headlines supported!
- Use **Ctrl+c Ctrl+n** to move to the next headline (any level); **Ctrl+c Ctrl+p** to the previous one.
- Use **Ctrl+c Ctrl+f** to move to the next headline (same level or higher level); **Ctrl+c Ctrl+b** to the previous one.
- Fixed a bug on bullet list. Thanks to quodlibet (fixed in v0.1.1).

### v0.1.0: Created!
- Smart Headline folding / unfolding is supported.
- Smart Lists is supported.

## Done
- **Smart Headline folding / unfolding**. Right now you can fold / unfold headlines by pressing **TAB** on it. I assume you use the following formats: # Section; ## Subsection; ### Subsubsection ...
- **Global Headline Folding / unfolding**. **Shift+Tab** to Fold / Unfold all at any position.
- **Smart Order / Unordered list**. When editing lists, you can just press **ENTER** and this plugin will automatically continue the list. Once the content of the list becomes empty it will stop.
- **Move between headlines**.
	- Use **Ctrl+c Ctrl+n** to move to the next headline (any level); **Ctrl+c Ctrl+p** to the previous one, for Mac. (**Ctrl+; Ctrl+n** and **Ctrl+; Ctrl+p** for Windows and Linux)
	- Use **Ctrl+c Ctrl+f** to move to the next headline (same level or higher level); **Ctrl+c Ctrl+b** to the previous one, for Mac. (**Ctrl+; Ctrlf** and **Ctrl+; Ctrl+b** for Windows and Linux)
- **Adjust headline level** Added by [David Smith](https://github.com/djs070).
    - **Super+Shift+,** for decreasing and **Super+Shift+.** for increasing headline levels.
- **Smart table**
	- Currently, the smart table suppose only the Grid table format of [Pandoc](http://johnmacfarlane.net/pandoc/README.html). Use monospaced fonts, otherwise it would appear bizarre.
	- The behavior is like the table in Org-mode. If you are unfamiliar with Org-mode, just use | (vertical line) to separate the column (e.g. | header1 | header 2 |), and use the **TAB** to reformat the table at point. Everything would fall into the place. Add +- and then press TAB for adding separator between rows. Add += and then press TAB for adding separator between header and the table body. Read the Grid tables section of [Pandoc Userg's Guide](http://johnmacfarlane.net/pandoc/README.html#tables) for more information.
	- Use **TAB** to move forward a cell in table, **Shift+TAB** to move backward.
	- Personally I plan to use grid table as a basis and add command for converting to other table formats if necessary.
- **Basic Pandoc integration with Pandoc** By integrating [SublimePandoc](https://github.com/jclement/SublimePandoc). Added by [DanielMe](https://github.com/DanielMe/).
	- **Note**: If you need to generate PDF output, please make sure you have pdflatex available ([MacTeX](http://www.tug.org/mactex/2012/) for Mac, or TeX Live for other OS). Please also specify "tex_path" in the package settings (Preference - Package Settings - SmartMarkdown - Settings - User (see Settings - Default as an example.))

## Todo
- **Embeded R & Python Code for reproducible research**
- **Better Pandoc integration** Actual support for different Pandoc command line options etc.
- ...


## For Developers
- Whenever possible, please obey the [PEP 8](http://www.python.org/dev/peps/pep-0008/) style guide. This can be checked easily with the plugin SublimeLinter.
- git-flow is recommended (but not enforced) as a development work flow. For instruction please read [Why aren't you using git-flow?](http://jeffkreeftmeijer.com/2010/why-arent-you-using-git-flow/). To adapt it, a command line tool [gitflow](https://github.com/nvie/gitflow/) is highly recommended.
- Please work on the develop branch, it's newer than master. the master branch is for users.

# License
The plugin is licensed under the MIT license.


Copyright (C) <2012> Muchenxuan Tong <demon386@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
