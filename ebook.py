# - * - encoding: utf-8 - * -

import requests
from bs4 import BeautifulSoup
from os.path import basename


class WikiUtils(object):

    @classmethod
    def download_image(cls, image_url):
        r = requests.get(image_url)
        image_url = image_url.replace("%27", "_")
        image_name = basename(image_url)
        with open("images/%s" % image_name, "wb") as image:
            image.write(r.content)
        return image_name

    @classmethod
    def html_tag_to_markdown(cls, tag, figures):
        text = ""
        class_ = tag.attrs.get("class", [])
        if tag.name == "p" and "caption" not in class_:
            text = tag.text.strip() + "\n\n"
        elif tag.name == "h3":
            text = "\n**%s**\n\n" % tag.text.strip()
        elif tag.name == "dt":
            text = "*%s*\n\n" % tag.text.strip()
        else:
            text, figures = cls.parse_image_related_tags(tag, figures)

        return text, figures

    @classmethod
    def parse_image_related_tags(cls, tag, figures):
        text = ""
        if tag.name == "figure":
            link = tag.find("a")
            image = link.attrs['href']
            figcaption = tag.find("figcaption")
            caption = figcaption.find("p", class_="caption")
            if caption:
                caption = caption.text
            else:
                caption = ""
            figures.append({
                'image': image,
                'caption': caption,
            })
        elif tag.name == "a":
            href = tag.attrs['href']
            image_tag = tag.find("img")
            if image_tag and tag.parent.name != "figure":
                width = int(image_tag.attrs.get("width", "0"))
                if width > 90:  # filter out profile pics
                    image_name = WikiUtils.download_image(href)
                    text = "\n![](images/%s)\n\n" % image_name
        return text, figures

    @staticmethod
    def parse_figures(figures):
        if figures is None:
            return ""

        text = "\n"
        for f in figures:
            image_name = WikiUtils.download_image(f['image'])
            text += "![%(caption)s](images/%(name)s)\n\n" % {
                'caption': f['caption'],
                'name': image_name
            }

        return text


def loop_until_tag(text, figures, firstElement, lastElement):
    new_text, figures = WikiUtils.html_tag_to_markdown(firstElement, figures)
    text += new_text

    if (firstElement.find_next() == lastElement):
        return text + WikiUtils.parse_figures(figures)
    else:
        return loop_until_tag(text, figures, firstElement.find_next(),
                              lastElement)


class WikiPage(object):

    def __init__(self, url):
        self.url = url

    def get_markdown(self):
        markdown = ""
        r = requests.get(self.url)

        soup = BeautifulSoup(r.content)
        contents = soup.find_all(class_="mw-headline")

        first_h2 = contents[0].parent
        next_h2 = first_h2.find_next("h2")

        while next_h2:
            markdown += "\n## %s\n" % first_h2.text.strip()
            text = loop_until_tag("", [], first_h2.find_next(), next_h2)
            first_h2 = next_h2
            next_h2 = next_h2.find_next("h2")
            markdown += "%s" % text

        return markdown


def create_book_markdown():
    joj_list = ("http://leagueoflegends.wikia.com/wiki/"
                "Category:The_Journal_of_Justice_Issues")

    r = requests.get(joj_list)
    soup = BeautifulSoup(r.content)

    link_list = soup.find(id="Volume_One").find_next()
    links = link_list.find_all("a")

    markdown = "% Journal of Justice\n"
    for l in links:
        link = "http://leagueoflegends.wikia.com%s " % l.attrs['href']
        print(link)
        markdown += "# %s\n" % l.text
        markdown += WikiPage(link).get_markdown()

    return markdown.encode("utf-8")

if __name__ == "__main__":
    with open("ebook.txt", "wb") as book:
        book.write(create_book_markdown())
