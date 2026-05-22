from parser.cleaner import strip_leading_comma


def test_leading_comma_stripped():
    assert strip_leading_comma(',"35.1","10.8"') == '"35.1","10.8"'


def test_only_one_comma_removed():
    assert strip_leading_comma(',,"x"') == ',"x"'


def test_line_without_leading_comma_unchanged():
    assert strip_leading_comma('"35.1","10.8"') == '"35.1","10.8"'


def test_header_line_unchanged():
    header = '"Time","Logger Temperature","External Voltage"'
    assert strip_leading_comma(header) == header
