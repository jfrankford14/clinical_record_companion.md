from xml.etree import ElementTree as ET

_Element = ET.Element


class XMLSyntaxError(ET.ParseError):
    """Fallback XML syntax error when native lxml is unavailable."""


class XMLParser:
    def __init__(self, recover: bool = False):
        self.recover = recover


def fromstring(text: bytes | str, parser: XMLParser | None = None) -> _Element:
    data = text.encode("utf-8") if isinstance(text, str) else text
    try:
        return ET.fromstring(data)
    except ET.ParseError as exc:
        if parser is not None and getattr(parser, "recover", False):
            return ET.Element("ClinicalDocument")
        raise XMLSyntaxError(str(exc)) from exc
