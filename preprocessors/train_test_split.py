import os
import json
import shutil
import argparse
import random


def process_dir(dir_path, split, file_type="yaml"):
    # create train and test directories
    parent_dir = os.path.abspath(os.path.join(dir_path, os.pardir))
    train_dir = os.path.join(parent_dir, "train")
    test_dir = os.path.join(parent_dir, "test")
    if not os.path.exists(train_dir):
        os.makedirs(train_dir)
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    # get all the filenames and split
    filenames = filter(lambda x: x.split('.')[-1] == file_type, os.listdir(dir_path))
    random.shuffle(filenames)
    split_val = int(len(filenames) * split)
    train_files = filenames[:split_val]
    test_files = filenames[split_val:]
    for t in train_files:
        shutil.copy(os.path.join(dir_path, t), os.path.join(train_dir, t))
    for t in test_files:
        shutil.copy(os.path.join(dir_path, t), os.path.join(test_dir, t))


def process_file(file_path):
    # to be implemented
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Splits the data in train and test')
    parser.add_argument('data', help='Path where the data lies. Can be both, a file or a directory')
    parser.add_argument('-s', '--split', default=0.9, help='Split ratio')
    args = parser.parse_args()

    with open("config.json") as conf_f:
        config = json.load(conf_f)

    if os.path.isdir(args.data):
        process_dir(args.data, args.split)
    else:
        process_file(args.data)
