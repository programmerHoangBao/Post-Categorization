from html import unescape
from html.parser import HTMLParser
import re

class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self._last_tag = None
        self._ignore_data = False
        self._pre = False

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        self._last_tag = tag
        if tag in ("br",):
            self.result.append("\n")
        elif tag in ("p","div","section","article","header","footer","h1","h2","h3","h4","h5","h6"):
            self._append_newline_if_needed()
        elif tag in ("li",):
            self.result.append("- ")
        elif tag in ("pre", "code"):
            self._pre = True
            self._append_newline_if_needed()
        elif tag in ("script","style"):
            self._ignore_data = True

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in ("p","div","section","article","header","footer","h1","h2","h3","h4","h5","h6"):
            self._append_newline_if_needed()
        elif tag in ("pre","code"):
            self._pre = False
            self._append_newline_if_needed()
        elif tag in ("script","style"):
            self._ignore_data = False
        elif tag in ("li",):
            self.result.append("\n")

    def handle_data(self, data):
        if self._ignore_data:
            return
        if self._pre:
            self.result.append(data)
        else:
            text = re.sub(r"\s+", " ", data)
            self.result.append(text)

    def handle_entityref(self, name):
        try:
            self.result.append(unescape("&%s;" % name))
        except Exception:
            pass

    def handle_charref(self, name):
        try:
            self.result.append(unescape("&#%s;" % name))
        except Exception:
            pass

    def _append_newline_if_needed(self):
        if len(self.result)==0:
            self.result.append("")
        if not self.result[-1].endswith("\n"):
            self.result.append("\n")

    def get_text(self):
        text = "".join(self.result)
        text = unescape(text)
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"\n{3,}", "\n\n", text)
        lines = [ln.rstrip() for ln in text.split("\n")]
        while lines and lines[0].strip()=="" :
            lines.pop(0)
        while lines and lines[-1].strip()=="" :
            lines.pop()
        return "\n".join(lines)
