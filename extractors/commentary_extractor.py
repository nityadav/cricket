from bs4 import BeautifulSoup
import urllib2
import json
import argparse


class CommentaryExtractor:
    def __init__(self):
        pass

    def extract(self, match_url):
        full_commentary = []
        for i in range(1, 5):
            innings_commentary = self.__extract_commentary__(match_url + "?innings=" + str(i) + ";view=odi_commentary")
            if innings_commentary:
                full_commentary.append(innings_commentary)
            else:
                break
        return json.dumps(full_commentary)

    def __extract_commentary__(self, url):
        commentary_html = urllib2.urlopen(url).read()
        match_soup = BeautifulSoup(commentary_html, "html.parser")
        commentary_event_divs = match_soup.find_all('div', attrs={'class': 'odi_commentary-event'})
        commentary_events = [{'over': self.__extract_over_num__(div.find('div', attrs={'class': 'odi_commentary-overs'})), 'text': self.__extract_commentary_text__(div.find('div', attrs={'class': 'odi_commentary-text'}))} for div in commentary_event_divs]
        return commentary_events

    @staticmethod
    def __extract_over_num__(comm_over_div):
        if comm_over_div:
            return float(comm_over_div.get_text())
        else:
            return -1.0

    @staticmethod
    def __extract_commentary_text__(comm_text_div):
        return comm_text_div.find('p').get_text()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract commentaries from a list of match urls')
    parser.add_argument('input_file', help='File consisting of match urls, one per line')
    parser.add_argument('output_dir', help='Output directory where all the odi_commentary data will be extracted')
    args = parser.parse_args()
    with open(args.input_file) as url_file:
        all_odis_url = filter(None, map(lambda x: x.strip(), url_file.readlines()))

    comm_extractor = CommentaryExtractor()

    for url in all_odis_url:
        comm_data = comm_extractor.extract(url)
        if comm_data == "[]":
            print "No odi_commentary data in: " + url
        else:
            match_id = url.split('/')[-1].split('.')[0]
            with open(args.output_dir + "/" + match_id + ".json", 'w') as comm_file:
                comm_file.write(comm_data)
