
import re
from bs4 import BeautifulSoup, Tag
from abc import ABC, abstractmethod

class BaseParser(ABC):
    _doc_link: str = ""
    _raw_html: str = ""
    _soup: BeautifulSoup = None

    def __init__(self, doc_link: str = "", raw_html: str = "", soup: BeautifulSoup = None):
        self._doc_link = doc_link
        self._raw_html = raw_html
        if soup:
            self._soup = soup
        elif raw_html:
            self._soup = BeautifulSoup(re.sub(r"<!--[\s\S\n]*?-->", "", raw_html), features="lxml")

    def _pre_do(self, text: str) -> str:
        """部分文档需要在返回前做格式处理"""
        return text
    
    def _parse_link(self, tag: Tag):
        # href = urljoin(self._doc_link, tag.get("href"))
        title = tag.get_text(strip=False)
        yield f"[{self._pre_do(title)}]({tag.get('href')}) "


    @abstractmethod
    def invoke(self) -> str:
        pass

    @property
    def doc_link(self):
        return self._doc_link
    
    @property
    def raw_html(self):
        return self._raw_html
    
    @property
    def soup(self):
        return self._soup
    
    @doc_link.setter
    def doc_link(self, doc_link: str):
        self._doc_link = doc_link

    @raw_html.setter
    def raw_html(self, raw_html: str):
        self._raw_html = raw_html
        self._soup = BeautifulSoup(raw_html, features="lxml")

    @soup.setter
    def soup(self, soup: BeautifulSoup):
        self._soup = soup
        self._raw_html = soup.prettify()

    def _parse_table(self, tag: Tag):
        # thead = tag.find("thead")
        headers = tag.find_all("th")
        # header_exists = isinstance(thead, Tag)
        yield "<table>"
        if headers:
            # headers = tag.find_all("th")
            if headers:
                yield "<tr>\n<th>\n"
                yield " </th>\n<th> ".join(self._pre_do(header.get_text()) for header in headers)
                yield " </th>\n</tr>\n"
                # yield "| "
                # yield " | ".join("----" for _ in headers)
                # yield "</tr>\n"

        tbody = tag.find("tbody")
        tbody_exists = isinstance(tbody, Tag)
        if tbody_exists:
            for row in tbody.find_all("tr"):
                yield "<tr>\n"
                for cell in row.find_all("td"):
                    yield f"<td>\n\n{''.join(self._parse_tag(cell)).strip()}\n\n</td>\n"
                # yield " </td>\n<td> ".join(
                #     re.sub(r"^\n\s+", "\n", " ".join(self._parse_tag(cell)).replace(r"\n\s+", "\n") ) for cell in row.find_all("td")
                # )
                yield "</tr>\n"
        yield "</table>"

        yield "\n\n"

        # re.sub(r"^\n\s+", "\n", " ".join(self._parse_tag(cell)).replace(r"\n\s+", "\n") )


