from keras.models import Model, load_model
from keras.layers import Input, Dense, LSTM
import numpy as np

from generators import odi_prediction_generators
from transformers import odi_prediction_xformers

import argparse
import json
import os
import logging


def get_data_for_prediction(data_dir):
    sub_innings_list, totals_list, sub_totals_list = [], [], []
    for inn1, inn2, result, summary, url in odi_prediction_generators.generate_match_data(data_dir):
        xformed_inn1 = odi_prediction_xformers.get_random_part(inn1, summary[0])
        if xformed_inn1:
            sub_innings_list += xformed_inn1[0]
            totals_list += xformed_inn1[1]
            sub_totals_list += xformed_inn1[2]
            # xformed_inn2 = odi_prediction_xformers.get_random_part(inn2, summary[1])
    return np.array(sub_innings_list), np.array(totals_list), np.array(sub_totals_list)


def get_baseline_model(inning_shape=(50, 2)):
    inp = Input(shape=inning_shape)
    net = LSTM(128)(inp)
    net = Dense(128, activation='relu', kernel_initializer='normal')(net)
    output = Dense(1, kernel_initializer='normal')(net)
    m = Model(inputs=inp, outputs=output)
    m.compile(loss='mean_squared_error', optimizer='rmsprop')
    return m


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train cricket prediction model')
    parser.add_argument('-t', '--train', action='store_true', help='Train the model and store in the location')
    parser.add_argument('-e', '--extract', action='store_true', help='Only data extraction')
    parser.add_argument('-s', '--story', action='store_true', help='Over by over prediction')
    parser.add_argument('--train_data', default="data/prediction/tensors/train", help='')
    parser.add_argument('--test_data', default="data/prediction/tensors/test", help='')
    parser.add_argument('--inning_tensor', default="innings.npy", help='')
    parser.add_argument('--subtotal_tensor', default="subtotal.npy", help='')
    parser.add_argument('--total_tensor', default="total.npy", help='')
    parser.add_argument('--model_file', default="models/prediction/model.h5", help='')
    args = parser.parse_args()

    with open("config.json") as conf_f:
        config = json.load(conf_f)
    task_config = config["tasks"]["odi_prediction"]

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    if args.extract:
        inn, total, subtotal = get_data_for_prediction(task_config["train_dir"])
        np.save(os.path.join(args.train_data, args.inning_tensor), inn)
        np.save(os.path.join(args.train_data, args.total_tensor), total)
        np.save(os.path.join(args.train_data, args.subtotal_tensor), subtotal)
        inn, total, subtotal = get_data_for_prediction(task_config["test_dir"])
        np.save(os.path.join(args.test_data, args.inning_tensor), inn)
        np.save(os.path.join(args.test_data, args.total_tensor), total)
        np.save(os.path.join(args.test_data, args.subtotal_tensor), subtotal)
    elif args.train:
        inns = np.load(os.path.join(args.train_data, args.inning_tensor))
        totals = np.load(os.path.join(args.train_data, args.total_tensor))
        subtotals = np.load(os.path.join(args.train_data, args.subtotal_tensor))
        assert inns.shape[0] == totals.shape[0] == subtotals.shape[0]
        if os.path.isfile(args.model_file):
            logging.info("Model file found at %s" % args.model_file)
            model = load_model(args.model_file)
        else:
            logging.info("Model file not found at %s. Starting training from beginning." % args.model_file)
            model = get_baseline_model()
        model.fit(inns, totals, batch_size=10, epochs=30)
        model.save(args.model_file)
    elif args.story:
        story_file = os.path.join(task_config['test_dir'], '291367.yaml')
        inn1, inn2, result, summary = odi_prediction_generators.get_match_data(story_file, True)
        if os.path.isfile(args.model_file):
            model = load_model(args.model_file)
        else:
            raise IOError('No model found. Either train the model or specify correct path of the model')
        for num_overs in range(len(inn1)):
            sub_inn = inn1[:num_overs + 1]
            runs, wkts = sub_inn[-1]
            sub_inn += [[0, 0]] * (50 - len(sub_inn))
            assert len(sub_inn) == 50
            pred_total = model.predict(np.array([sub_inn]), batch_size=1).tolist()[0][0]
            logging.info("Over score: %s Predicted total: %d" % (str(runs) + "/" + str(wkts), int(pred_total)))
    else:
        inns = np.load(os.path.join(args.test_data, args.inning_tensor))
        totals = np.load(os.path.join(args.test_data, args.total_tensor))
        subtotals = np.load(os.path.join(args.test_data, args.subtotal_tensor))
        assert inns.shape[0] == totals.shape[0] == subtotals.shape[0]
        if os.path.isfile(args.model_file):
            model = load_model(args.model_file)
        else:
            raise IOError('No model found. Either train the model or specify correct path of the model')
        actual_totals = totals.tolist()
        sub_totals = subtotals.tolist()
        pred_totals = model.predict(inns).tolist()
        assert len(actual_totals) == len(pred_totals)
        for a, s, p in zip(actual_totals, sub_totals, pred_totals):
            print a, s, p
