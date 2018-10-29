import os

test_dir = 'data/prediction/test'
files = filter(lambda x: x != '.DS_Store', os.listdir(test_dir))
urls = map(lambda x: "http://www.espncricinfo.com/ci/engine/match/%s.html" % x.split('.')[0], files)
with open('test_urls.txt', 'w') as u:
    u.write('\n'.join(urls))
