import datetime
from bs4 import BeautifulSoup,Doctype, SoupStrainer, Tag, NavigableString
from typing import Generator
from da.document.parser.base import BaseParser
from da.logger import logger
import re



class PythonDocumentParser(BaseParser):
    def invoke(self) -> str:
        # logger.debug(f"load url:{self._doc_link}")
        content = self._soup.find('div', class_='body')
        joined = "".join(self._parse_tag(content))
        return re.sub(r"\n\n+", "\n\n", joined).strip()
    
    
    def _pre_do(self, text: str) -> str:
        # 处理部分情况两个下划线__在markdown显示不出来的问题
        text = re.sub(r"__(?P<key>\w+)__", "\\_\\_<key>\\_\\_", text)
        # 处理部分情况两个星号**在markdown显示不出来的问题，比如10的二次方（10**2）
        text = re.sub(r"(?P<number1>\d+)\*\*(?P<number2>\d+)", "<number1>\\\*\\*<number2>", text)
        return text
    
    def _parse_tag(self, tag:Tag) -> Generator[str, None, None]:
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
                yield self._pre_do(child)
            elif isinstance(child, Tag):
                if child.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                    h = child
                    [_h.decompose() for _h in h.find_all("a", class_="headerlink")]
                    yield f"{'#' * int(h.name[1:])} {self._pre_do(h.get_text())}\n\n"
                elif child.name == "a":
                    if "headerlink" in child.get_attribute_list("class", []):
                        continue
                    yield from self._parse_link(child)
                elif child.name == "img":
                    yield f"![{self._pre_do(child.get('alt', ''))}]({child.get('src')})"
                elif child.name in ["strong", "b"] \
                    or ("rubric" in child.get_attribute_list("class", [])):
                    yield f"**{self._pre_do(child.get_text(strip=False))}**"
                elif child.name in ["em", "i"]:
                    yield f"_{self._pre_do(child.get_text(strip=False))}_"
                elif child.name == "br":
                    yield "\n"
                elif child.name == "p":
                    yield "".join(self._parse_tag(child)).replace("\n", " ")
                    # yield from self._parse_tag(child)
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
                elif child.name == "table":
                    yield from self._parse_table(child)
                elif child.name == "pre":
                    # 获取第一个元素节点
                    first_element = child.find(True)
                    if first_element and first_element.name and first_element.name == "strong":
                        yield from self._parse_grammar(child)
                    else:
                        yield self._pre_do(child.get_text(strip=True))
                elif (child.name == "div" and "seealso" in child.get_attribute_list("class", []))\
                    or (child.name == "div" and "versionadded" in child.get_attribute_list("class", []))\
                    or (child.name == "div" and "versionchanged" in child.get_attribute_list("class", []))\
                    or child.name == "blockquote":
                    yield from self._parse_seealso(child)
                elif child.name == "div" and " ".join(child.attrs.get("class", "")).find("highlight-") >= 0:
                    yield from self._parse_code(child)
                elif child.name == "dl":
                    yield from self._parse_term(child)
                elif child.name in ["button"]:
                    continue
                else:
                    yield from self._parse_tag(child)

    def _parse_seealso(self, tag: Tag)-> Generator[str, None, None]:
        if tag.name == "blockquote":
            joined = "\n\n".join([self._pre_do(_tag.get_text()) for _tag in tag.find_all("p")])
            yield "    >" + re.sub(r"\n", "\n    >", joined).strip() + "\n"
        else:
            joined = self._pre_do("\n".join(self._parse_tag(tag)))
            yield "> " + re.sub(r"\n", "\n> ", re.sub(r"\n\n", "\n", joined).strip()) + "\n"
        # yield re.sub(r"\n>\s\n>\s+", "\n> \n> ", text).strip()

    def _parse_term(self, tag: Tag) -> Generator[str, None, None]:
        """术语解析"""
        if "field-list" in tag.get_attribute_list("class", []):
            for child in tag:
                if child.name == "dt":
                    texts = "".join(self._parse_tag(child)).strip('\n')
                    yield f"**{self._pre_do(texts)}:** "
                elif child.name == "dd":
                    texts = "".join(self._parse_tag(child))
                    # 定义行首增加4个空格
                    yield f"{self._pre_do(texts)}\n"
        else:
            for child in tag:
                if child.name == "dt":
                    texts = "".join(self._parse_tag(child)).strip('\n')
                    yield f"**{self._pre_do(texts)}**\n<br>"
                elif child.name == "dd":
                    texts = "".join(self._parse_tag(child))
                    # 定义行首增加4个空格
                    yield f"&#160;&#160;&#160;&#160;{self._pre_do(texts)}\n"

    def _parse_link(self, tag: Tag):
        # href = urljoin(self._doc_link, tag.get("href"))
        title = tag.get_text(strip=False)
        yield f"[{self._pre_do(title)}]({tag.get('href')})"

    def _parse_grammar(self, tag: Tag) -> Generator[str, None, None]:
        grammars = ["```"]
        grammar = []
        for child in tag.children:
            if child.name == "strong" and re.match("grammar-token-python", child.get("id", "")):
                if len(grammar):
                    grammars.append(" ".join(grammar))
                    grammar = []
                grammar.append(child.get_text())
            elif isinstance(child, NavigableString):
                grammar.append(child)
            elif child.children:
                grammar.append("".join(self._parse_tag(child)))
            else:
                grammar.append(child.get_text(strip=True))
        if len(grammar):
            grammars.append(" ".join(grammar))
            grammar = []

        grammars.append("```")
        yield re.sub(r"\n+", "\n", "\n".join(grammars))

    def _parse_code(self, tag: Tag) -> Generator[str, None, None]:
        classes = tag.attrs.get("class", "")
        # [_tag.decompose() for _tag in tag.find_all("span", class_="gp")]

        language = next(
            filter(lambda x: re.match(r"highlight-\w+", x), classes),
            None,
        )
        if language is None:
            language = ""
        else:
            language = language.split("-")[1]

        language = "python" if language.find("python") >= 0 or language.find("py") >= 0 else language
        code_text = tag.find("pre").get_text()
        yield f"```{language}\n{code_text}```"

    
    @staticmethod
    def extractor(raw_html: str) -> str:
        # logger.info(k)
        parser = PythonDocumentParser(raw_html=raw_html)
        return parser.invoke()


class PythonDocumentMetadata(BaseParser):
    def invoke(self):
        lang, description, framework_ver = "", "", ""
        try:
            lang = self._soup.find("html").get("lang", "")
        except:
            pass

        try:
            description = self._soup.find("meta", attrs={"name": "Description"}).get("content", "")
        except:
            try:
                description = self._soup.find("div", class_="body").find("p", class_=False).get_text(strip=True)
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
            "framework": "python",
            "framework_ver": framework_ver,
            "add_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
        }
    
    @staticmethod
    def extractor(raw_html: str, url: str) -> dict:
        parser = PythonDocumentMetadata(raw_html=raw_html, doc_link=url)
        return parser.invoke()

