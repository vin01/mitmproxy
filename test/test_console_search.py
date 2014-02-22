
import sys
import libmproxy.console.contentview as cv
from libmproxy import utils, flow, encoding
import tutils

def test_search_highlights():
    # Default text in requests is content. We will search for nt once, and
    # expect the first bit to be highlighted. We will do it again and expect the
    # second to be.
    f = tutils.tflowview()

    f.search("nt")
    text_object = tutils.get_body_line(f.last_displayed_body, 0)
    assert text_object.get_text() == ('content', [(None, 2), (f.highlight_color, 2)])

    f.search("nt")
    text_object = tutils.get_body_line(f.last_displayed_body, 1)
    assert text_object.get_text() == ('content', [(None, 5), (f.highlight_color, 2)])

def test_search_returns_useful_messages():
    f = tutils.tflowview()

    # original string is content. this string should not be in there.
    test_string = "oranges and other fruit."
    response = f.search(test_string)
    assert response == "no matches for '%s'" % test_string

def test_search_highlights_clears_prev():
    f = tutils.tflowview(request_contents="this is string\nstring is string")

    f.search("string")
    text_object = tutils.get_body_line(f.last_displayed_body, 0)
    assert text_object.get_text() == ('this is string', [(None, 8), (f.highlight_color, 6)])

    # search again, it should not be highlighted again.
    f.search("string")
    text_object = tutils.get_body_line(f.last_displayed_body, 0)
    assert text_object.get_text() != ('this is string', [(None, 8), (f.highlight_color, 6)])

def test_search_highlights_multi_line():
    f = tutils.tflowview(request_contents="this is string\nstring is string")

    # should highlight the first line.
    f.search("string")
    text_object = tutils.get_body_line(f.last_displayed_body, 0)
    assert text_object.get_text() == ('this is string', [(None, 8), (f.highlight_color, 6)])

    # should highlight second line, first appearance of string.
    f.search("string")
    text_object = tutils.get_body_line(f.last_displayed_body, 1)
    assert text_object.get_text() == ('string is string', [(None, 0), (f.highlight_color, 6)])

    # should highlight third line, second appearance of string.
    f.search("string")
    text_object = tutils.get_body_line(f.last_displayed_body, 1)
    print(text_object.get_text(), ('string is string', [(None, 10), (f.highlight_color, 6)]))
    assert text_object.get_text() == ('string is string', [(None, 10), (f.highlight_color, 6)])

def test_search_loops():
    f = tutils.tflowview(request_contents="this is string\nstring is string")

    # get to the end.
    f.search("string")
    f.search("string")
    f.search("string")

    # should highlight the first line.
    message = f.search("string")
    text_object = tutils.get_body_line(f.last_displayed_body, 0)
    assert text_object.get_text() == ('this is string', [(None, 8), (f.highlight_color, 6)])
    assert message == "search hit BOTTOM, continuing at TOP"

def test_search_focuses():
    f = tutils.tflowview(request_contents="this is string\nstring is string")

    # should highlight the first line.
    f.search("string")

    # should be focusing on the 2nd text line.
    f.search("string")
    text_object = tutils.get_body_line(f.last_displayed_body, 1)
    assert f.last_displayed_body.focus == text_object

def test_search_does_not_crash_on_bad():
    """
        this used to crash, kept for reference.
    """

    f = tutils.tflowview(request_contents="this is string\nstring is string\n"+("A" * cv.VIEW_CUTOFF)+"AFTERCUTOFF")
    f.search("AFTERCUTOFF")

    # pretend F
    f.state.add_flow_setting(
        f.flow,
        (f.state.view_flow_mode, "fullcontents"),
        True
    )
    f.master.refresh_flow(f.flow)

    # text changed, now this string will exist. can happen when user presses F
    # for full text view
    f.search("AFTERCUTOFF")

def test_search_backwards():
    f = tutils.tflowview(request_contents="content, content")

    first_match = ('content, content', [(None, 2), (f.highlight_color, 2)])

    f.search("nt")
    text_object = tutils.get_body_line(f.last_displayed_body, 0)
    assert text_object.get_text() == first_match

    f.search("nt")
    text_object = tutils.get_body_line(f.last_displayed_body, 1)
    assert text_object.get_text() == ('content, content', [(None, 5), (f.highlight_color, 2)])

    f.search_again(backwards=True)
    text_object = tutils.get_body_line(f.last_displayed_body, 0)
    assert text_object.get_text() == first_match

def test_search_back_multiline():
    f = tutils.tflowview(request_contents="this is string\nstring is string")

    f.search("string")
    text_object = tutils.get_body_line(f.last_displayed_body, 0)
    first_match = ('this is string', [(None, 8), (f.highlight_color, 6)])
    assert text_object.get_text() == first_match

    f.search_again()
    text_object = tutils.get_body_line(f.last_displayed_body, 1)
    assert text_object.get_text() == ('string is string', [(None, 0), (f.highlight_color, 6)])

    f.search_again(backwards=True)
    text_object = tutils.get_body_line(f.last_displayed_body, 0)
    assert text_object.get_text() == first_match
