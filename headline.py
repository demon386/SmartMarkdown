"""Some utility functions for working with headline of Markdown.

Terminologies
- Headline :: The headline entity of the text of the headline
- Content :: The content under the current headline. It stops after
  encountering a headline with the same level of EOF.
"""
# Author: Muchenxuan Tong <demon386@gmail.com>

import re

import sublime


MATCH_PARENT = 1
MATCH_CHILD = 2
MATCH_SILBING = 3
MATCH_ANY = 4
ANY_LEVEL = -1


def extract_level_from_headline(headline):
    """Extract the level of headline, None if not found.

    """
    re_string = _get_re_string(ANY_LEVEL, None)
    match = re.match(re_string, headline)

    if match:
        return len(match.group(1))
    else:
        return None


def region_of_content_of_headline_at_point(view, from_point):
    """Used to extract region of the folded headline."""
    _, level = headline_and_level_at_point(view, from_point)
    if level == None:
        return None

    if is_content_empty_at_point(view, from_point):
        return None

    line_num, _ = view.rowcol(from_point)
    content_line_start_point = view.text_point(line_num + 1, 0)

    next_headline, _ = find_next_headline(view,
                                          content_line_start_point,
                                          level,
                                          MATCH_PARENT)
    if next_headline != None:
        end_pos = next_headline.a - 1
    else:
        end_pos = view.size()
    return sublime.Region(content_line_start_point, end_pos)


def headline_and_level_at_point(view, from_point, search_above_and_down=False):
    """Return the current headline and level.

    If it's in a headline, then return the level of the headline.
    Otherwise depends on the argument it might search above and down
    """

    line_region = view.line(from_point)
    line_content = view.substr(line_region)
    # Update the level in case it's headline.ANY_LEVEL
    level = extract_level_from_headline(line_content)

    # Search above and down
    if not level and search_above_and_down:
        # Search above
        headline_region, _ = find_previous_headline(view,\
                                                    from_point,\
                                                    ANY_LEVEL,
                                                    skip_folded=True)
        line_content, level = headline_and_level_at_point(view, headline_region.a)
        # Search down
        if level is None:
            headline_region, _ = find_next_headline(view,\
                                                    from_point,\
                                                    ANY_LEVEL,
                                                    skip_folded=True)
            line_content, level = headline_and_level_at_point(view, headline_region.a)

    return line_content, level


def is_content_empty_at_point(view, from_point):
    """Check if the next line is a headline at the same level"""
    _, level = headline_and_level_at_point(view, from_point)
    line_num, _ = view.rowcol(from_point)
    next_line_region = view.line(view.text_point(line_num + 1, 0))
    next_line_content = view.substr(next_line_region)
    next_line_level = extract_level_from_headline(next_line_content)

    if next_line_level and next_line_level <= level:
        # Return True otherwise a '\t' would be insert
        return True
    else:
        return False


def _get_re_string(level, match_type=None):
    """Get the compiled regular expression pattern according to match type.

    Return regular expression string, rather than compiled string. Since
    sublime's view.find function needs string.

    Parameters
    ----------
    match_type: int
        MATCH_PARENT, MATCH_CHILD, or MATCH_SILBING

    """
    if level == ANY_LEVEL:
        re_string = r'^(#+)\s.*'
    else:
        try:
            if match_type == MATCH_PARENT:
                re_string = r'^(#{1,%d})\s.*' % level
            elif match_type == MATCH_CHILD:
                re_string = r'^(#{%d,})\s.*' % level
            elif match_type == MATCH_SILBING:
                re_string = r'^(#{%d,%d})\s.*' % (level, level)
        except ValueError:
            print("match_type has to be specified if level isn't ANY_LEVE")
    return re_string


def _get_new_point_if_already_in_headline(view, from_point, forward=True):
    line_content = view.substr(view.line(from_point))
    if extract_level_from_headline(line_content):
        line_num, _ = view.rowcol(from_point)
        if forward:
            return view.text_point(line_num + 1, 0)
        else:
            return view.text_point(line_num, 0) - 1
    else:
        return from_point


def _is_region_folded(region, view):
    for i in view.folded_regions():
        if i.contains(region):
            return True
    return False


def find_next_headline(view, from_point, level, match_type=None,
                       skip_headline_at_point=False,
                       skip_folded=False):
    """Return the region of the next headline or EOF.

    Parameters
    ----------
    view: sublime.view

    from_point: int
        From which to find.

    level: int
        The beginning headline level to match.

    match_type: int
        MATCH_PARENT, MATCH_CHILD, or MATCH_SILBING.
        Could be None if level is ANY_LEVEL.

    skip_headline_at_point: boolean
        When searching whether skip the headline at point

    skip_folded: boolean
        Whether to skip the folded region

    Returns
    -------
    match_region: int
        Matched region, or None if not found.

    match_level: int
        The level of matched headline, or None if not found.

    """
    if skip_headline_at_point:
        # Move the point to the next line if we are
        # current in a headline already.
        from_point = _get_new_point_if_already_in_headline(view, from_point,
                                                           forward=True)

    ## Use view.find to find the region
    re_string = _get_re_string(level, match_type)
    match_region = view.find(re_string, from_point)
    if skip_folded:
        while (match_region and _is_region_folded(match_region, view)):
            from_point = match_region.b
            match_region = view.find(re_string, from_point)

    if match_region:
        ## Extract the level of matched headlines according to the region
        headline = view.substr(match_region)
        match_level = extract_level_from_headline(headline)
    else:
        match_level = None
    return (match_region, match_level)


def find_previous_headline(view, from_point, level, match_type=None,
                           skip_headline_at_point=False,
                           skip_folded=False):
    """Return the region of the previous headline or EOF.

    Parameters
    ----------
    view: sublime.view

    from_point: int
        From which to find.

    level: int
        The beginning headline level to match.

    match_type: int
        MATCH_PARENT, MATCH_CHILD, or MATCH_SILBING
        Could be None if level is ANY_LEVEL.

    skip_headline_at_point: boolean
        When searching whether skip the headline at point

    skip_folded: boolean
        Whether to skip the folded region

    Returns
    -------
    match_region: int
        Matched region, or None if not found.

    match_level: int
        The level of matched headline, or None if not found.

    """
    if skip_headline_at_point:
        # Move the point to the previous lineif we are
        # current in a headline already.
        from_point = _get_new_point_if_already_in_headline(view, from_point,\
                                                           forward=False)

    re_string = _get_re_string(level, match_type)
    all_match_regions = view.find_all(re_string)

    match_region = _get_neraest_previous_match_region(from_point,\
                                                      all_match_regions,\
                                                      view,\
                                                      skip_folded)
    if match_region:
        ## Extract the level of matched headlines according to the region
        headline = view.substr(match_region)
        match_level = extract_level_from_headline(headline)
    else:
        match_level = None
    return (match_region, match_level)


def _get_neraest_previous_match_region(from_point, all_match_regions, view, \
                                       skip_folded):
    """Find the nearest previous  matched region among all matched regions.

    None if not found.

    """
    nearest_region = None

    for r in all_match_regions:
        if r.b <= from_point and (not nearest_region or r.a > nearest_region.a):
            if skip_folded and not _is_region_folded(r, view):
                nearest_region = r

    return nearest_region
