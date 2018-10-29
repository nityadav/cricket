import argparse
import os
import json
import numpy as np
from keras.models import load_model
from keras.models import Model
from keras.layers import Input, Dense, LSTM, concatenate

TRAIN_DIR = "train"
TEST_DIR = "test"
INNING1_FILE = "inn1.txt"
INNING2_FILE = "inn2.txt"
RESULT_FILE = "results.txt"
URLS_FILE = "urls.txt"
MODEL_FILE = "model/model10.h5"


def get_baseline_model(inning_shape=(50, 2)):
    inn = Input(shape=inning_shape)
    net = LSTM(10)(inn)
    net = Dense(10)(net, activation='relu', kernel_initializer='normal')
    output = Dense(1, kernel_initializer='normal')(net)
    model = Model(inputs=inn, outputs=output)
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model


def get_model():
    inn1 = Input(shape=(50, 2))
    inn2 = Input(shape=(50, 2))
    shared_lstm = LSTM(10)
    encoded_inn1 = shared_lstm(inn1)
    encoded_inn2 = shared_lstm(inn2)
    merged_inngs = concatenate([encoded_inn1, encoded_inn2], axis=-1)
    prediction = Dense(1, activation='sigmoid')(merged_inngs)
    model = Model(inputs=[inn1, inn2], outputs=prediction)
    model.compile(optimizer='rmsprop',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
    return model


def flatmap(list_of_lists):
    return [i for l in list_of_lists for i in l]


def get_data(data_dir, expand=False):
    if expand:
        expansion_factor = 5
        with open(os.path.join(data_dir, INNING1_FILE)) as inn1_f:
            inn1 = np.array(np.repeat(map(do_padding, map(json.loads, inn1_f.readlines())), expansion_factor))
        with open(os.path.join(data_dir, INNING2_FILE)) as inn2_f:
            inn2 = np.array(flatmap(map(break_innings, map(json.loads, inn2_f.readlines()))))
        with open(os.path.join(data_dir, RESULT_FILE)) as res_f:
            labels = np.array(np.repeat(map(lambda x: int(x.strip()), res_f.readlines()), expansion_factor))
        with open(os.path.join(data_dir, URLS_FILE)) as urls_f:
            urls = np.repeat(map(lambda x: x.strip(), urls_f.readlines()), expansion_factor).tolist()
    else:
        with open(os.path.join(data_dir, INNING1_FILE)) as inn1_f:
            inn1 = np.array(map(do_padding, map(json.loads, inn1_f.readlines())))
        with open(os.path.join(data_dir, INNING2_FILE)) as inn2_f:
            inn2 = np.array(map(do_padding, map(json.loads, inn2_f.readlines())))
        with open(os.path.join(data_dir, RESULT_FILE)) as res_f:
            labels = np.array(map(lambda x: int(x.strip()), res_f.readlines()))
        with open(os.path.join(data_dir, URLS_FILE)) as urls_f:
            urls = map(lambda x: x.strip(), urls_f.readlines())
    print inn1.shape, inn2.shape, labels.shape
    assert inn1.shape[0] == inn2.shape[0] == labels.shape[0], "labels should be same in number as examples"
    return inn1, inn2, labels, urls


def do_padding(list_of_overs):
    num_overs = len(list_of_overs)
    return list_of_overs + [[0, 0]] * (50 - num_overs)


def break_innings(inn_data):
    """
    Break the innings data into a list of sub-innings
    :param inn_data: 
    :return: 
    """
    overs_delimiter = 10
    new_inn_data = do_padding(inn_data)
    return [do_padding(new_inn_data[:i]) for i in range(10, 51, overs_delimiter)]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train and evaluate cricket prediction models')
    parser.add_argument('-t', dest='train', action='store_true', help='Train the mode')
    args = parser.parse_args()

    if args.train:
        inn1_train, inn2_train, result_train, _ = get_data(TRAIN_DIR, True)
        match_pred_model = get_model()
        match_pred_model.fit([inn1_train, inn2_train], result_train, batch_size=5, validation_split=0.2, epochs=10)
        match_pred_model.save(MODEL_FILE)
    else:
        match_pred_model = load_model(MODEL_FILE)
        inn1_test, inn2_test, result_test, urls_test = get_data(TEST_DIR)
        pred = match_pred_model.predict([inn1_test, inn2_test]).tolist()
        for i, res in enumerate(result_test.tolist()):
            if res != int(round(pred[i][0])):
                print i, res, int(round(pred[i][0]))
