import json
from asciitree import LeftAligned, LegacyStyle, draw_tree
from collections import OrderedDict


def change_dict(data_dict):
    for key, value in data_dict.items():
        if isinstance(value, str):

            # For filename and links
            data_dict[key] = OrderedDict([
                (value, {})
            ])

            # for filenames only
            data_dict[key] ={}
        else:
            change_dict(value)


def print_folder_data(data_dict):
    change_dict(data)
    print(LeftAligned()(data))


def save_file_folder_data(data_dict):
    change_dict(data)
    with open("tree.md", 'w', encoding='utf-8') as target:
        target.write(LeftAligned()(data))


if __name__ == '__main__':
    data = json.load(open('data.json'))
    data = OrderedDict([
        ('asciitree', data)
    ])
    save_file_folder_data(data)
