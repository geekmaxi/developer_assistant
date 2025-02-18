
import datetime
import re
from .base import BaseParser
from bs4 import BeautifulSoup,Doctype, SoupStrainer, Tag, NavigableString

class LangchainDocumentParser(BaseParser):
    def invoke(self) -> str:
        # logger.debug(f"load url:{self._doc_link}")
        SCAPE_TAGS = ["nav", "footer", "aside", "script", "style"]
        [tag.decompose() for tag in self.soup.find_all(SCAPE_TAGS)]

        content = self._soup.find('div', class_='theme-doc-markdown')
        joined = "".join(self._parse_tag(content))
        return re.sub(r"\n\n+", "\n\n", joined).strip()
    
    def _parse_tag(self, tag):
        for child in tag.children:
            if isinstance(child, Doctype):
                continue

            if isinstance(child, NavigableString):
                yield child
            elif isinstance(child, Tag):
                if child.name == "section":
                    yield self._parse_tag(child)
                if child.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                    yield f"{'#' * int(child.name[1:])} {child.get_text()}\n\n"
                elif child.name == "a":
                    yield f"[{child.get_text(strip=False)}]({child.get('href')})"
                elif child.name == "img":
                    yield f"![{child.get('alt', '')}]({child.get('src')})"
                elif child.name in ["strong", "b"] or (child.name == "div" and "rubric" in child.get_attribute_list("class", [])):
                    yield f"**{child.get_text(strip=False)}**"
                elif child.name in ["em", "i"]:
                    yield f"_{child.get_text(strip=False)}_"
                elif child.name == "br":
                    yield "\n"
                elif child.name == "code":
                    parent = child.find_parent()
                    if parent is not None and parent.name == "pre":
                        classes = parent.attrs.get("class", "")

                        language = next(
                            filter(lambda x: re.match(r"language-\w+", x), classes),
                            None,
                        )
                        if language is None:
                            language = ""
                        else:
                            language = language.split("-")[1]

                        lines: list[str] = []
                        for span in child.find_all("span", class_="token-line"):
                            line_content = "".join(
                                token.get_text() for token in span.find_all("span")
                            )
                            lines.append(line_content)

                        code_content = "\n".join(lines)
                        yield f"```{language}\n{code_content}\n```\n\n"
                    else:
                        yield f"`{child.get_text(strip=False)}`"

                elif child.name == "p":
                    yield from self._parse_tag(child)
                    yield "\n\n"
                elif child.name == "ul":
                    for li in child.find_all("li", recursive=False):
                        yield "- "
                        yield from self._parse_tag(li)
                        yield "\n\n"
                elif child.name == "ol":
                    for i, li in enumerate(child.find_all("li", recursive=False)):
                        yield f"{i + 1}. "
                        yield from self._parse_tag(li)
                        yield "\n\n"
                elif child.name == "div" and "tabs-container" in child.attrs.get(
                    "class", [""]
                ):
                    tabs = child.find_all("li", {"role": "tab"})
                    tab_panels = child.find_all("div", {"role": "tabpanel"})
                    for tab, tab_panel in zip(tabs, tab_panels):
                        tab_name = tab.get_text(strip=True)
                        yield f"{tab_name}\n"
                        yield from self._parse_tag(tab_panel)
                elif child.name == "table":
                    thead = child.find("thead")
                    header_exists = isinstance(thead, Tag)
                    if header_exists:
                        headers = thead.find_all("th")
                        if headers:
                            yield "| "
                            yield " | ".join(header.get_text() for header in headers)
                            yield " |\n"
                            yield "| "
                            yield " | ".join("----" for _ in headers)
                            yield " |\n"

                    tbody = child.find("tbody")
                    tbody_exists = isinstance(tbody, Tag)
                    if tbody_exists:
                        for row in tbody.find_all("tr"):
                            yield "| "
                            yield " | ".join(
                                cell.get_text(strip=True) for cell in row.find_all("td")
                            )
                            yield " |\n"

                    yield "\n\n"
                elif child.name in ["button"]:
                    continue
                    
                else:
                    yield from self._parse_tag(child)

    @staticmethod
    def extractor(input: any) -> str:
        # logger.info(k)
        if type(input) == BeautifulSoup:
            parser = LangchainDocumentParser(soup=input)
        else:
            parser = LangchainDocumentParser(raw_html=input)
        return parser.invoke()
    
class LangchainDocumentMetadata(BaseParser):
    def invoke(self):
        lang, description, framework_ver = "", "", ""
        try:
            lang = self._soup.find("html").get("lang", "")
        except:
            pass

        try:
            description = self._soup.find("meta", attrs={"name": "description"}).get("content", "")
        except:
            try:
                description = self._soup.find("div", class_="theme-doc-markdown markdown").find("p", class_=False).get_text(strip=True)
            except:
                pass
            pass
        

        try:
            pattern = r"/([0-9\.]+)/"
            match = re.search(pattern, self.doc_link)
            framework_ver = match.group(1)
        except:
            pass

        return {
            "source": self._doc_link,
            "title": self._soup.title.string if self._soup.title else "",
            "description": description,
            "language": lang,
            "framework": "langchain",
            "framework_ver": framework_ver,
            "add_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
        }
    
    @staticmethod
    def extractor(raw_html: str, url: str) -> dict:
        parser = LangchainDocumentMetadata(raw_html=raw_html, doc_link=url)
        return parser.invoke()