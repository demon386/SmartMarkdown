# SmartMarkdown for Sublime Text 2

Author: Muchenxuan Tong (demon386 at gmail.com)

## Introduction
The plugin is aimed at making editing Markdown in Sublime Text 2 easier and more powerful. Ideally, I hope we can bring several amazing features of [Org-mode](http://org-mode.org) of Emacs into Sublime Text 2.

## Done
- **Smart Headline folding / unfolding**. Right now you can fold / unfold headlines by pressing **TAB** on it. I assume you use the following formats: # Section; ## Subsection; ### Subsubsection ...
- **Global Headline Folding / unfolding**. **Shift+Tab** to Fold / Unfold all at any position.
- **Smart Order / Unordered list**. When editing lists, you can just press **ENTER** and this plugin will automatically continue the list. Once the content of the list becomes empty it will stop.
- **Move between headlines**.
	- Use **Ctrl+c Ctrl+n** to move to the next headline (any level); **Ctrl+c Ctrl+p** to the previous one.
	- Use **Ctrl+c Ctrl+f** to move to the next headline (same level or higher level); **Ctrl+c Ctrl+b** to the previous one.
- **Basic Pandoc integration with Pandoc** By integrating [SublimePandoc](https://github.com/jclement/SublimePandoc). Added by [DanielMe](https://github.com/DanielMe/).

## Todo
- **Smart Table**
- **Embeded R & Python Code for reproducible research**
- **Better Pandoc integration** Actual support for different Pandoc command line options etc.
- ...

## What's new
### v0.1.3: Add support for global headling folding / unfolding.
### v0.1.2: Move between headlines supported!
- Use **Ctrl+c Ctrl+n** to move to the next headline (any level); **Ctrl+c Ctrl+p** to the previous one.
- Use **Ctrl+c Ctrl+f** to move to the next headline (same level or higher level); **Ctrl+c Ctrl+b** to the previous one.
- Fixed a bug on bullet list. Thanks to quodlibet (fixed in v0.1.1).

### v0.1.0: Created!
- Smart Headline folding / unfolding is supported.
- Smart Lists is supported.

# License
The plugin is licensed under the MIT license.


Copyright (C) <2012> <demon386 at gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
