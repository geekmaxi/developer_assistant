import datetime
import re
from typing import Generator

from bs4 import Doctype, Tag, NavigableString

from da.logger import logger
from .base import BaseParser

class FastapiDocumentParser(BaseParser):
    def invoke(self) -> str:
        content_tag = self._soup.find('article', class_='md-content__inner')
        cls = content_tag.get_attribute_list("class")
        joined = "".join(self._parse_tag(content_tag))
        return re.sub(r"\n\n+", "\n\n", joined).strip()
    
    def _pre_do(self, text:str) -> str:
        return text
    
    def _parse_tag(self, tag:Tag, level: int = 0):
        if tag is None:
            yield ""
        try:
            tag.children
        except:
            logger.error("Tag.children.")
            return
        for child in tag.children:
            if isinstance(child, Doctype):
                continue
            if isinstance(child, NavigableString):
                yield self._pre_do(child.strip())
            elif isinstance(child, Tag):
                if child.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                    h = child
                    [_h.decompose() for _h in h.find_all("a", class_="headerlink")]
                    yield f"{'#' * int(h.name[1:])} "
                    if child and child.children:
                        yield from self._parse_tag(child)
                    else:
                        yield f"{self._pre_do(h.get_text())}"

                    yield f"\n\n"
                elif child.name == "a":
                    yield from self._parse_link(child)
                elif child.name == "img":
                    yield f"![{self._pre_do(child.get('alt', ''))}]({child.get('src')})"
                elif child.name in ["strong", "b"]\
                    or ("rubric" in child.get_attribute_list("class", [])):
                    yield f"**{self._pre_do(child.get_text(strip=False))}**"
                elif child.name == "p":
                    # if child.children:
                    # logger.info(child.get_text(strip=True))
                    yield " ".join(self._parse_tag(child)).replace("\n", " ")
                    # yield from self._parse_tag(child)
                    yield "\n\n"
                elif child.name in ["strong", "b"]:
                    yield f"**{self._pre_do(child.get_text(strip=False))}**"
                elif child.name in ["em", "i"]:
                    yield f"_{self._pre_do(child.get_text(strip=False))}_"
                elif child.name == "code":
                    _classes = child.get_attribute_list("class", [])
                    _watcher = ["doc-symbol-class", "doc-symbol-attribute", "doc-symbol-method"]
                    intersection = list(set(_classes) & set(_watcher)) #交集
                    if len(intersection):
                        for _i in intersection:
                            # 使用 re.findall() 和索引提取最后一个单词。
                            words = re.findall(r"\b\w+\b", _i)  # 查找所有单词
                            yield f"```{words[-1]}``` "
                    else:
                        yield f"```{self._pre_do(child.get_text(strip=True))}``` "
                elif child.name == "div" and "highlight" in child.get_attribute_list("class", []):
                    yield from self._parse_code(child)
                elif child.name == "details":
                    
                    if child.find("summary"):
                        yield f"> {self._pre_do(child.find('summary').get_text())}\n\n"
                    # yield from self._parse_tag(child.find("summary"))
                elif child.name == "table":
                    yield from self._parse_table(child)
                elif child.name == "ul":
                    if child.parent.name == "li":
                        level = level + 1
                    for li in child.find_all("li", recursive=False):
                        yield f"\n{'    ' * level}- "
                        yield from self._parse_tag(li, level)
                        yield "\n\n"
                elif child.name == "ol":
                    for i, li in enumerate(child.find_all("li", recursive=False)):
                        yield f"{i + 1}. "
                        yield from self._parse_tag(li)
                        yield "\n\n"
                elif child.name == "span":
                    yield from self._parse_tag(child)
                elif child.name == "hr":
                    yield "\n----------------------------\n"
                elif child.name in ["button"] or (child.name == "form" and "md-feedback" in child.get_attribute_list("class", [])):
                    continue
                # elif child.name == "div":
                #     yield from self._parse_tag(child)
                else:
                   yield from self._parse_tag(child)

    def _parse_code(self, tag: Tag) -> Generator[str, None, None]:
        code_tag = tag.find("code")

        if code_tag:
            yield "```python\n"
            yield code_tag.get_text()
            yield "```\n\n"
        else:
            yield ""

    def _parse_link(self, tag: Tag):
        # href = urljoin(self._doc_link, tag.get("href"))
        title = tag.get_text(strip=False)
        yield f"[{self._pre_do(title)}]({tag.get('href')})"

    @staticmethod
    def extractor(raw_html: str) -> str:
        parser = FastapiDocumentParser(raw_html=raw_html)
        return parser.invoke()
    

class FastapiDocumentMeta(BaseParser):
    def invoke(self):
        lang, description, framework_ver = "", "", ""
        try:
            lang = self._soup.find("html").get("lang", "")
        except:
            pass

        try:
            description = self._soup.find("meta", attrs={"name": "description"}).get("content", "")
        except:
            pass
        

        try:
            # logger.info(self._soup.find("div", class_="md-header__source"))
            ver = self._soup.find("div", class_="md-header__source").find("li", class_=lambda x: x and 'md-source__fact--version' in x)
            framework_ver = ver.get_text(strip=True) if ver else "0.115.8"
        except:
            pass

        return {
            "source": self._doc_link,
            "title": self._soup.title.string if self._soup.title else "",
            "description": description,
            "language": lang,
            "framework": "fastapi",
            "framework_ver": framework_ver,
            "add_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
        }
    
    @staticmethod
    def extractor(raw_html: str, url: str) -> dict:
        parser = FastapiDocumentMeta(raw_html=raw_html, doc_link=url)
        return parser.invoke()