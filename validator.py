import csv
import random

from input.input_data import sven_genes


def read_tsv(file_path):
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        tsv_reader = csv.reader(file, delimiter='\t')
        curated_act = []
        curated_rep = []
        for row in tsv_reader:
            if row[2] == 'Activation':
                curated_act.append(row[0:2])
            if row[2] == 'Repression':
                curated_rep.append(row[0:2])
        act_dict = {}
        rep_dict = {}
        for x in curated_act:
            if x[0] in act_dict:
                act_dict[x[0]].append(x[1])
            else:
                act_dict[x[0]] = [x[1]]
        for x in curated_rep:
            if x[0] in rep_dict:
                rep_dict[x[0]].append(x[1])
            else:
                rep_dict[x[0]] = [x[1]]
        tf_list = set(act_dict.keys())
        tf_list.update(set(rep_dict.keys()))
        total_dict = {}
        for x in tf_list:
            if x in act_dict:
                total_dict[x] = act_dict[x]
            else:
                total_dict[x] = []
            if x in rep_dict:
                total_dict[x] += rep_dict[x]

        return tf_list, total_dict
        #return tf_list, act_dict, rep_dict



