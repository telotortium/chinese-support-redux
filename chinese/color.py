# Copyright © 2012 Thomas TEMPÉ <thomas.tempe@alysse.org>
# Copyright © 2017-2019 Joseph Lorimer <joseph@lorimer.me>
#
# This file is part of Chinese Support Redux.
#
# Chinese Support Redux is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Chinese Support Redux is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Chinese Support Redux.  If not, see <https://www.gnu.org/licenses/>.

from re import IGNORECASE, sub

from .consts import (
    COLOR_RUBY_TEMPLATE,
    COLOR_TEMPLATE,
    half_ruby_regex,
    HANZI_RANGE,
    jyutping_regex,
    pinyin_regex,
    ruby_regex,
)
from .hanzi import split_hanzi
from .sound import extract_tags
from .transcribe import tone_number, sanitize_transcript
from .util import align, is_punc, no_color


def colorize(words, target='pinyin', ruby_whole=False):
    from .ruby import has_ruby

    assert isinstance(words, list)

    def colorize_ruby_sub(p):
        return '<span class="tone{t}">{r}</span>'.format(
            t=tone_number(p.group(2)), r=p.group()
        )

    def colorize_trans_sub(text, pattern):
        def repl(p):
            return '<span class="tone{t}">{r}</span>'.format(
                t=tone_number(p.group(1)), r=p.group()
            )

        colorized = ''
        for s in text.split():
            colorized += sub(pattern, repl, s, IGNORECASE)
        return colorized

    colorized = []
    for text in words:
        text = no_color(text)
        (text, sound_tags) = extract_tags(text)

        if has_ruby(text):
            if ruby_whole:
                text = sub(ruby_regex, colorize_ruby_sub, text, IGNORECASE)
            else:
                text = colorize_trans_sub(text, half_ruby_regex)
        elif target == 'pinyin':
            text = colorize_trans_sub(text, pinyin_regex)
        elif target == 'jyutping':
            text = colorize_trans_sub(text, jyutping_regex)
        else:
            raise NotImplementedError(target)

        colorized.append(text + sound_tags)

    return ' '.join(colorized)


def colorize_dict(text):
    assert isinstance(text, str)

    def _sub(p):
        s = ''
        hanzi = p.group(1)
        pinyin = sanitize_transcript(p.group(2), 'pinyin', grouped=False)
        delim = '|'

        if hanzi.count(delim) == 1:
            hanzi = hanzi.split(delim)
            s += colorize_fuse(
                split_hanzi(hanzi[0], grouped=False), pinyin, True
            )
            s += delim
            s += colorize_fuse(
                split_hanzi(hanzi[1], grouped=False), pinyin, False
            )
        else:
            s += colorize_fuse(split_hanzi(hanzi, grouped=False), pinyin, True)

        return s

    return sub(r'([\%s|]+)\[(.*?)\]' % HANZI_RANGE, _sub, text)


def colorize_fuse(chars, trans, ruby=False):
    assert isinstance(chars, list)
    assert isinstance(trans, list)

    colorized = ''

    for c, t in align(chars, trans):
        if c is None or t is None:
            continue
        if is_punc(c) and is_punc(t):
            colorized += c
            continue
        if ruby:
            colorized += COLOR_RUBY_TEMPLATE.format(
                tone=tone_number(t), chars=c, trans=t
            )
        else:
            colorized += COLOR_TEMPLATE.format(tone=tone_number(t), chars=c)

    return colorized
