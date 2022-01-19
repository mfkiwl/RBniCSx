# Copyright (C) 2021-2022 by the minirox authors
#
# This file is part of minirox.
#
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Tests for minirox.io.text_line module."""

import minirox.io


def test_text_line() -> None:
    """Unit test for TextLine.__str__."""
    greet = "Hello, World!"
    fill = "#"
    text_line = minirox.io.TextLine(greet, fill=fill)
    text_line_str = str(text_line)
    text_line_len = len(text_line_str)
    first_space = text_line_str.find(" ")
    assert first_space >= 0
    last_space = text_line_str.rfind(" ")
    assert first_space >= 0
    assert text_line_str[:first_space] == fill * first_space
    assert text_line_str[last_space + 1:] == fill * (text_line_len - last_space - 1)
    assert text_line_str[first_space + 1:last_space] == greet
