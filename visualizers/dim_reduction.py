import gensim


model_path = "models/commentary_word2vec.model"

model = gensim.models.Word2Vec.load(model_path)

print model.wv.most_similar(positive=['good-length'])

# print model.wv.most_similar(positive=['pulled'])
# print model.wv.most_similar(positive=['driven'])
