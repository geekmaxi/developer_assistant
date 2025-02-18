import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup,Doctype, SoupStrainer, Tag, NavigableString
from typing import Generator
from da.document.parser.base import BaseParser
from da.logger import logger
import re



class W3schoolDocumentParser(BaseParser):
    def invoke(self) -> str:
        # logger.debug(f"load url:{self._doc_link}")
        content_tag = self._soup.find('div', id='main')
        try:
            [tag.decompose() for tag in content_tag.find_all(["style", "form", "video", "input"])]
            # 删除头部banner、中部广告、能力测试, 
            [tag.decompose() for tag in content_tag.find_all('div', id=re.compile(r"mainLeaderboard|midcontentadcontainer|exercisecontainer|yt_container|user-profile-bottom-wrapper", re.IGNORECASE))]
            [tag.decompose()  for tag in content_tag.find_all("div", class_="yt_container")]
            # [tag.decompose() for tag in content_tag.find_all("div", id="midcontentadcontainer")]
            [tag.decompose() for tag in content_tag.find_all(class_=re.compile(r"w3-btn|ws-btn|ga-featured|ga-youtube", re.IGNORECASE))]
            # [tag.decompose() for tag in content_tag.find_all(name="div", class_="w3-panel w3-leftbar w3-theme-l4 w3-hide-large w3-hide-medium")]
            # [tag.decompose() for tag in content_tag.find_all(name="div", class_="w3-panel w3-leftbar w3-theme-l4 w3-hide-small")]
            # [tag.decompose() for tag in content_tag.find_all(name="div", class_="w3-panel")]
            [tag.decompose() for tag in content_tag.find_all(string=re.compile(r"Click on the \"Try it Yourself\" button to see how it works.|My Learning|Log in to your account, and start earning points!|^Video:"))]
            [tag.decompose() for tag in content_tag.find_all(string=re.compile(r'quiz', re.IGNORECASE))]
            # [tag.decompose() for tag in content_tag.find_all(name="div", class_="nextprev")]
        except BaseException as e:
            logger.error(f"Tag.find_all.{self._soup.get_text()}")
            return ""
            

        joined = "".join(self._parse_tag(content_tag))
        return re.sub(r"^#+ $", "", re.sub(r"\n\n+", "\n\n", joined).strip())
    
    def _parse_tag(self, tag: Tag):
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
                _classes = child.get_attribute_list("class", [])
                if child.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                    h = child
                    [_h.decompose() for _h in h.find_all("a", class_="headerlink")]
                    yield f"\n{'#' * int(h.name[1:])} "
                    if child and child.children:
                        yield from self._parse_tag(child)
                    else:
                        yield f"{self._pre_do(h.get_text())}"

                    yield f"\n\n"
                elif child.name == "a":
                    yield from self._parse_link(child)
                elif child.name == "img":
                    yield f"![{self._pre_do(child.get('alt', ''))}]({child.get('src')})"
                elif child.name in ["strong", "b"]:
                    text = child.get_text(strip=False)
                    yield f"**{self._pre_do(text)}**" if text else ""
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

                elif (child.name == "div" and "w3-code" in child.get_attribute_list("class", [])) \
                    or (child.name == "code"):
                    yield from self._parse_code(child)
                # elif child.name == "code":
                #     yield f"```{child.get_text(strip=True)}```"
                elif child.name == "table":
                    yield from self._parse_table(child)
                elif child.name == "div" and list(set(_classes) & set(["w3-example", "w3-note"])):
                    yield from self._parse_quote(child)
                elif child.name == "label":
                    yield f"{child.get_text(strip=True)} | "
                else:
                    yield from self._parse_tag(child)
    def _parse_quote(self, tag: Tag) -> Generator[str, None, None]:
        children = self._parse_tag(tag)
        yield "\n\n> " + re.sub(r"\n", "\n> ", re.sub(r"\n\n", "\n", "".join(children))) + "\n"

    def _pre_do(self, text):
        return re.sub("<", "\<", re.sub(">", "\>", text))
    
    def _parse_code(self, tag: Tag) -> Generator[str, None, None]:
        # code_tag = tag.find("div", class_="w3-code")
        classes = tag.get_attribute_list("class", [])
        _classes = " ".join(classes)

        lang_match = re.match(r".*(html|sql|css|js|python|java)High.*", _classes)
        lang_match_v2 = re.match(r".*language-(java|php|csharp|jsx|django).*", _classes)
        if lang_match and lang_match_v2:
            language = lang_match.group(1) if lang_match else lang_match_v2.group(1)
            yield f"```{language}\n"
            for child in tag.children:
                if child.name == 'br':
                    yield "\n"
                else:
                    yield child.get_text(strip=False).replace("\n", "")
            yield "\n```\n\n"
        else:
            yield f"```{tag.get_text(strip=True)}```"

    @staticmethod
    def extractor(raw_html: str) -> str:
        # logger.info(k)
        parser = W3schoolDocumentParser(raw_html=raw_html)
        return parser.invoke()
    

class W3schoolDocumentMetadata(BaseParser):
    def invoke(self):
        lang, description, framework_ver = "", "", ""

        try:
            lang = self._soup.find("html").get("lang", "")
        except:
            pass

        try:
            description = self._soup.find("div", id="main").find("p", class_="intro").get_text(strip=True).replace("\n", " ")
        except BaseException as e:
            # logger.exception(e)
            try:
                description = self._soup.find("meta", attrs={"name": re.compile(r"^description$", re.IGNORECASE)}).attrs['content']
            except:
                pass
            pass
        

        try:
            _ret = urlparse(self.doc_link)
            framework = _ret.path.split("/")[1].lower()
        except:
            pass

        return {
            "source": self._doc_link,
            "title": self._soup.title.string if self._soup.title else "",
            "description": description,
            "language": lang,
            "framework": framework,
            "framework_ver": framework_ver,
            "add_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
        }
    
    @staticmethod
    def extractor(raw_html: str, url: str) -> dict:
        parser = W3schoolDocumentMetadata(raw_html=raw_html, doc_link=url)
        return parser.invoke()