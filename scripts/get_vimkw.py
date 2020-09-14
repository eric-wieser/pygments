import re

from pygments.util import format_lines

r_line = re.compile(r"^(syn keyword vimCommand contained|syn keyword vimOption "
                    r"contained|syn keyword vimAutoEvent contained)\s+(.*)")
r_item = re.compile(r"(\w+)(?:\[(\w+)\])?")

HEADER = '''\
# -*- coding: utf-8 -*-
"""
    pygments.lexers._vim_builtins
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is autogenerated by scripts/get_vimkw.py

    :copyright: Copyright 2006-2020 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

# Split up in multiple functions so it's importable by jython, which has a
# per-method size limit.
'''

METHOD = '''\
def _get%(key)s():
%(body)s
    return var
%(key)s = _get%(key)s()
'''

def getkw(input, output):
    out = file(output, 'w')

    # Copy template from an existing file.
    print(HEADER, file=out)

    output_info = {'command': [], 'option': [], 'auto': []}
    for line in file(input):
        m = r_line.match(line)
        if m:
            # Decide which output gets mapped to d
            if 'vimCommand' in m.group(1):
                d = output_info['command']
            elif 'AutoEvent' in m.group(1):
                d = output_info['auto']
            else:
                d = output_info['option']

            # Extract all the shortened versions
            for i in r_item.finditer(m.group(2)):
                d.append('(%r,%r)' %
                         (i.group(1), "%s%s" % (i.group(1), i.group(2) or '')))

    output_info['option'].append("('nnoremap','nnoremap')")
    output_info['option'].append("('inoremap','inoremap')")
    output_info['option'].append("('vnoremap','vnoremap')")

    for key, keywordlist in output_info.items():
        keywordlist.sort()
        body = format_lines('var', keywordlist, raw=True, indent_level=1)
        print(METHOD % locals(), file=out)

def is_keyword(w, keywords):
    for i in range(len(w), 0, -1):
        if w[:i] in keywords:
            return keywords[w[:i]][:len(w)] == w
    return False

if __name__ == "__main__":
    getkw("/usr/share/vim/vim74/syntax/vim.vim",
          "pygments/lexers/_vim_builtins.py")
