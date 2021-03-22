#!/usr/bin/env python

"""
Simple tests for pelican_lunr plugin.
"""

import pelican.plugins.pelican_lunr


def test_lunr():
    """
    Ensure pelican-pelican_lunr plugin is loadable.
    """
    dir(pelican.plugins.pelican_lunr)
