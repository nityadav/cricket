from bs4 import BeautifulSoup
import urllib2, json

MAX_PAGE_NUM = 100

class MatchExtractor:
    def __init__(self):
        self.url = "http://stats.espncricinfo.com/ci/engine/stats/index.html?class=2;page=%d;spanmin1=%s;spanval1=span;template=results;type=aggregate;view=results"

    def extract(self, from_date="05+Jan+2005"):
        all_matches_urls_list = []
        for page_num in xrange(1, MAX_PAGE_NUM):
            complete_url = self.url % (page_num, from_date)
            match_urls_list = MatchExtractor.__get_match_urls__(complete_url)
            if not match_urls_list:
                break
            else:
                all_matches_urls_list += match_urls_list
        print '\n'.join(all_matches_urls_list)

    @staticmethod
    def __get_match_urls__(search_url):
        html_page = urllib2.urlopen(search_url).read()
        search_soup = BeautifulSoup(html_page, "html.parser")
        siteurl = "http://www.espncricinfo.com"
        return [siteurl + atag.get('href') for atag in search_soup.find_all("a", text="Match scorecard")]

m = MatchExtractor()
m.extract()