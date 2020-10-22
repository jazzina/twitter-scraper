from requests_html import HTMLSession, HTML
from lxml.etree import ParserError

session = HTMLSession()


class Profile:
    """
        Parse twitter profile and split informations into class as attribute.

        Attributes:
            - name
            - username
            - birthday
            - location
            - biography
            - website
            - profile_photo
            - banner_photo
            - likes_count
            - tweets_count
            - followers_count
            - following_count
            - is_verified
            - is_private
            - user_id
    """

    def __init__(self, username):
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": f"https://twitter.com/{username}",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8",
            "X-Twitter-Active-User": "yes",
            "X-Requested-With": "XMLHttpRequest",
            "Accept-Language": "en-US",
        }

        page = session.get(f"https://twitter.com/{username}", headers=headers)
        self.username = username
        self.__parse_profile(page)

    @staticmethod
    def _prepare_number(num_str):
        result = "".join([c for c in num_str if c.isdigit()])
        return result

    def __parse_profile(self, page):
        try:
            html = HTML(html=page.text, url="bunk", default_encoding="utf-8")
        except KeyError:
            raise ValueError(
                f'Oops! Either "{self.username}" does not exist or is private.'
            )
        except ParserError:
            pass
        except IndexError:
            pass

        try:
            self.is_private = html.find(".ProfileHeaderCard-badges .Icon--protected")[0]
            self.is_private = True
        except:
            self.is_private = False

        try:
            self.is_verified = html.find(".ProfileHeaderCard-badges .Icon--verified")[0]
            self.is_verified = True
        except:
            self.is_verified = False

        self.location = html.find(".ProfileHeaderCard-locationText")[0].text
        if not self.location:
            self.location = None

        self.birthday = html.find(".ProfileHeaderCard-birthdateText")[0].text
        if self.birthday:
            self.birthday = self.birthday.replace("Born ", "")
        else:
            self.birthday = None

        self.profile_photo = html.find(".ProfileAvatar-image")[0].attrs["src"]

        try:
            self.banner_photo = html.find(".ProfileCanopy-headerBg img")[0].attrs["src"]
        except KeyError:
            self.banner_photo = None

        page_title = html.find("title")[0].text
        self.name = page_title[: page_title.find("(")].strip()

        self.user_id = html.find(".ProfileNav")[0].attrs["data-user-id"]

        self.biography = html.find(".ProfileHeaderCard-bio")[0].text
        if not self.birthday:
            self.birthday = None

        self.website = html.find(".ProfileHeaderCard-urlText")[0].text
        if not self.website:
            self.website = None

        # get total tweets count if available
        try:
            q = html.find('li[class*="--tweets"] span[data-count]')[0].attrs["data-count"]
            self.tweets_count = int(q)
        except:
            self.tweets_count = None

        # get total following count if available
        try:
            q = html.find('li[class*="--following"] span[data-count]')[0].attrs["data-count"]
            self.following_count = int(q)
        except:
            self.following_count = None

        if self.following_count is None:
            q = page.find(attrs={"data-nav":"following"})
            if q:
                self.following_count = int(self._prepare_number(q.attrs["title"].split(' ')[0]))
            else:
                self.following_count = 0


        # get total follower count if available
        try:
            q = html.find('li[class*="--followers"] span[data-count]')[0].attrs["data-count"]
            self.followers_count = int(q)
        except:
            self.followers_count = None

        if self.followers_count is None:
            try:
                q=page.find(attrs={"data-nav":"followers"})
                self.followers_count = int(self._prepare_number(q.attrs["title"].split(' ')[0]))
            except:
                self.followers_count = 0

        # get total like count if available
        try:
            q = html.find('li[class*="--favorites"] span[data-count]')[0].attrs["data-count"]
            self.likes_count = int(q)
        except:
            self.likes_count = None
        
        if self.likes_count is None:
            q = page.find(attrs={"data-nav":"favorites"})
            if q:
                self.likes_count = int(self._prepare_number(q.attrs["title"].split(' ')[0].replace('.', '')))
            else:
                self.likes_count = 0

        # parse count of tweets
        q = page.find(attrs={"data-nav":"tweets"})

        self.tweets_count = int(self._prepare_number(q.attrs["title"].split(' ')[0]))

    def __process_paragraph(self, contents):
        output = ''
        links = []
        for i in contents:
            try:
                output+=i
            except:
                if i.name=="a":
                    tmp_txt, tmp_lnk = process_paragraph(i.contents)
                    links+=tmp_lnk
                    output+=tmp_txt#+'@['+i.attrs['href']+']'
                    links.append(i.attrs['href'])
                elif i.name in ['s', 'b']:
                    tmp_txt, tmp_lnk = process_paragraph(i.contents)
                    links+=tmp_lnk
                    output+=tmp_txt
        return output, links
    
    def to_dict(self):
        return dict(
            name=self.name,
            username=self.username,
            birthday=self.birthday,
            biography=self.biography,
            location=self.location,
            website=self.website,
            profile_photo=self.profile_photo,
            banner_photo=self.banner_photo,
            likes_count=self.likes_count,
            tweets_count=self.tweets_count,
            followers_count=self.followers_count,
            following_count=self.following_count,
            is_verified=self.is_verified,
            is_private=self.is_private,
            user_id=self.user_id
        )

    def __dir__(self):
        return [
            "name",
            "username",
            "birthday",
            "location",
            "biography",
            "website",
            "profile_photo",
            'banner_photo'
            "likes_count",
            "tweets_count",
            "followers_count",
            "following_count",
            "is_verified",
            "is_private",
            "user_id"
        ]

    def __repr__(self):
        return f"<profile {self.username}@twitter>"
