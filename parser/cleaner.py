def strip_leading_comma(line: str) -> str:
    return line[1:] if line.startswith(",") else line
