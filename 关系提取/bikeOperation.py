from urllib import parse
from bs4 import BeautifulSoup
from urllib import request


# 获取百度百科页面
def getBikePage(word):
    res = request.urlopen("https://baike.baidu.com/item/" + parse.quote(word))
    return res.read().decode()


# 解析html中class="para"的内容
def parsePara(node):
    paras = node.find_all(class_="para")
    content = ""
    for p in paras:
        content += p.text
    return content


# 解析百度百科中对词条的定义
def parseLemmaSummary(soup):
    ls = soup.find_all(class_="lemma-summary")
    if len(ls) > 0:
        text = parsePara(ls[0])
    else:
        text = ""
    return "leammaSummary\n" + text + "\n"


# 找到正文开始的节点,即LemmaSummary以下的部分
def getMainContentBegin(soup):
    catalog = soup.find(class_=u"lemmaWgt-lemmaCatalog")
    if catalog == None:
        catalog = soup.find(class_=u"basic-info cmn-clearfix")
    if catalog == None:
        catalog = soup.find(class_=u"edit-prompt")
    return catalog


# 传入百科词条，解析百度百科，将所有的一级标题下的内容分开存，并返回一级标题
def parseContent(bikeword):
    titleSet = set()
    html = getBikePage(bikeword)
    soup = BeautifulSoup(html, "lxml")
    content = parseLemmaSummary(soup)
    node = getMainContentBegin(soup).find_next_sibling()
    while (node != None):
        if 'class' in node.attrs and "level-2" in node.attrs['class']:
            title = node.text.replace(bikeword, "").replace("\n", "").replace("编辑", "")
            titleSet.add(title)
            content += title + "\n"
        elif 'class' in node.attrs and "para" in node.attrs['class']:
            content += node.text.replace("\n", "") + "\n"
        node = node.find_next_sibling()
    return titleSet, content


# 传入百科词条，解析该百科中所有外链百科词条
def parseOutLinkFromContent(bikeword):
    outLinkBikewords = set()

    html = getBikePage(bikeword)
    soup = BeautifulSoup(html, "lxml")
    node = getMainContentBegin(soup).find_next_sibling()
    while (node != None):
        if 'class' in node.attrs and "para" in node.attrs['class']:
            for a in node.find_all("a", href=True):
                outLinkBikewords.add(a.text)
        node = node.find_next_sibling()

    return outLinkBikewords

# titleet, content = parseContent("相反数")
# print(content)
parseOutLinkFromContent("相反数")
