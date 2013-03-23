"""Some utility functions for working with headline of Markdown.

Terminologies
- Headline :: The headline entity OR the text of the headline
- Content :: The content under the current headline. It stops after
  encountering a headline with the same or higher level OR EOF.
"""
# Author: Muchenxuan Tong <demon386@gmail.com>

import re
import sublime

try:
    from .utilities import is_region_void
except ValueError:
    from utilities import is_region_void

MATCH_PARENT = 1   # Match headlines at the same or higher level
MATCH_CHILD = 2    # Match headlines at the same or lower level
MATCH_SILBING = 3  # Only Match headlines at the same level.
MATCH_ANY = 4      # Any headlines would be matched.
ANY_LEVEL = -1     # level used when MATCH_ANY is used as match type


def region_of_content_of_headline_at_point(view, from_point):
    """Extract the region of the content of under current headline."""
    _, level = headline_and_level_at_point(view, from_point)
    if level == None:
        return None

    if is_content_empty_at_point(view, from_point):
        return None

    line_num, _ = view.rowcol(from_point)
    content_line_start_point = view.text_point(line_num + 1, 0)

    next_headline, _ = find_headline(view, \
                                     content_line_start_point, \
                                     level, \
                                     True, \
                                     MATCH_PARENT)
    if not is_region_void(next_headline):
        end_pos = next_headline.a - 1
    else:
        end_pos = view.size()
    return sublime.Region(content_line_start_point, end_pos)


def headline_and_level_at_point(view, from_point, search_above_and_down=False):
    """Return the current headline and level.

    If from_point is inside a headline, then return the headline and level.
    Otherwise depends on the argument it might search above and down.
    """
    line_region = view.line(from_point)
    line_content = view.substr(line_region)
    # Update the level in case it's headline.ANY_LEVEL
    level = _extract_level_from_headline(line_content)

    # Search above and down
    if level is None and search_above_and_down:
        # Search above
        headline_region, _ = find_headline(view,\
                                           from_point,\
                                           ANY_LEVEL,
                                           False,
                                           skip_folded=True)
        if not is_region_void(headline_region):
            line_content, level = headline_and_level_at_point(view,\
                                                              headline_region.a)
        # Search down
        if level is None:
            headline_region, _ = find_headline(view,\
                                               from_point,\
                                               ANY_LEVEL,
                                               True,
                                               skip_folded=True)
            if not is_region_void(headline_region):
                line_content, level = headline_and_level_at_point(view, headline_region.a)

    return line_content, level


def _extract_level_from_headline(headline):
    """Extract the level of headline, None if not found.

    """
    re_string = _get_re_string(ANY_LEVEL, MATCH_ANY)
    match = re.match(re_string, headline)

    if match:
        return len(match.group(1))
    else:
        return None


def is_content_empty_at_point(view, from_point):
    """Check if the content under the current headline is empty.

    For implementation, check if next line is a headline a the same
    or higher level.

    """
    _, level = headline_and_level_at_point(view, from_point)
    if level is None:
        raise ValueError("from_point must be inside a valid headline.")

    line_num, _ = view.rowcol(from_point)
    next_line_region = view.line(view.text_point(line_num + 1, 0))
    next_line_content = view.substr(next_line_region)
    next_line_level = _extract_level_from_headline(next_line_content)

    # Note that EOF works too in this case.
    if next_line_level and next_line_level <= level:
        return True
    else:
        return False


def find_headline(view, from_point, level, forward=True, \
                  match_type=MATCH_ANY, skip_headline_at_point=False, \
                  skip_folded=False):
    """Return the region of the next headline or EOF.

    Parameters
    ----------
    view: sublime.view

    from_point: int
        From which to find.

    level: int
        The headline level to match.

    forward: boolean
        Search forward or backward

    match_type: int
        MATCH_SILBING, MATCH_PARENT, MATCH_CHILD or MATCH_ANY.

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
                                                           forward)

    re_string = _get_re_string(level, match_type)
    if forward:
        match_region = view.find(re_string, from_point)
    else:
        all_match_regions = view.find_all(re_string)
        match_region = _nearest_region_among_matches_from_point(view, \
                                                                all_match_regions, \
                                                                from_point, \
                                                                False, \
                                                                skip_folded)

    if skip_folded:
        while (_is_region_folded(match_region, view)):
            from_point = match_region.b
            match_region = view.find(re_string, from_point)

    if not is_region_void(match_region):
        if not is_scope_headline(view, match_region.a):
            return find_headline(view, match_region.a, level, forward, \
                                 match_type, True, skip_folded)
        else:
            ## Extract the level of matched headlines according to the region
            headline = view.substr(match_region)
            match_level = _extract_level_from_headline(headline)
    else:
        match_level = None
    return (match_region, match_level)

def _get_re_string(level, match_type=MATCH_ANY):
    """Get regular expression string according to match type.

    Return regular expression string, rather than compiled string. Since
    sublime's view.find function needs string.

    Parameters
    ----------
    match_type: int
        MATCH_SILBING, MATCH_PARENT, MATCH_CHILD or ANY_LEVEL.

    """
    if match_type == MATCH_ANY:
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
    if _extract_level_from_headline(line_content):
        line_num, _ = view.rowcol(from_point)
        if forward:
            return view.text_point(line_num + 1, 0)
        else:
            return view.text_point(line_num, 0) - 1
    else:
        return from_point


def is_scope_headline(view, from_point):
    return view.score_selector(from_point, "markup.heading") > 0 or \
        view.score_selector(from_point, "meta.block-level.markdown") > 0


def _nearest_region_among_matches_from_point(view, all_match_regions, \
                                             from_point, forward=False,
                                             skip_folded=True):
    """Find the nearest matched region among all matched regions.

    None if not found.

    """
    nearest_region = None

    for r in all_match_regions:
        if not forward and r.b <= from_point and \
            (not nearest_region or r.a > nearest_region.a):
            candidate = r
        elif forward and r.a >= from_point and \
            (not nearest_region or r.b < nearest_region.b):
            candidate = r
        else:
            continue
        if skip_folded and not _is_region_folded(candidate, view):
            nearest_region = candidate

    return nearest_region


def _is_region_folded(region, view):
    for i in view.folded_regions():
        if i.contains(region):
            return True
    return False
