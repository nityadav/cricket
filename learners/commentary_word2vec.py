from collections import deque
import os
import json
import gensim


PUNCS = [',', '.', '?', '!']


class CommentarySentences(object):
    def __init__(self, json_dir):
        self.filepaths = [os.path.join(json_dir, filename) for filename in os.listdir(json_dir)]

    def __iter__(self):
        self.curr_file_idx = 0
        self.sentence_pool = deque()
        return self

    def next(self):
        if self.sentence_pool:
            return self.sentence_pool.popleft()
        else:
            while (self.curr_file_idx < len(self.filepaths)) and (not self.sentence_pool):
                self.__extract_sentences__()
                self.curr_file_idx += 1
            if self.sentence_pool:
                return self.sentence_pool.popleft()
            else:
                raise StopIteration

    def __extract_sentences__(self):
        curr_file_path = self.filepaths[self.curr_file_idx]
        with open(curr_file_path) as inp_f:
            json_str = inp_f.readline().strip()
            for inning_data in json.loads(json_str):
                for comm_item in inning_data:
                    if comm_item['over'] > 0:
                        comm_words = map(CommentarySentences.clean_word, ' '.join(comm_item['text'].split('\n')[2:]).split())
                        filtered_comm_words = filter(None, comm_words)
                        if filtered_comm_words:
                            self.sentence_pool.append(filtered_comm_words)

    @staticmethod
    def clean_word(word):
        word = word.strip().lower()
        while word and word[0] in PUNCS:
            word = word[1:]
        while word and word[-1] in PUNCS:
            word = word[:-1]
        return word


commentary = CommentarySentences("data/odi_commentary")
model = gensim.models.Word2Vec(commentary, workers=4)
model.save('commentary_word2vec.model')
