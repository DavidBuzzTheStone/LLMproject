import random

from get_response import get_response, results_to_dictionary, supervisor_query_expander, gene_query_with_format_check, \
  default_query_with_supervisions
import pandas as pd
import py4cytoscape as p4c
import numpy as np
from typing import Optional
import json
from typing import TextIO
import ast

from input.input_data import sven_genes
from validator import read_tsv
import matplotlib.pyplot as plt
from matplotlib_venn import venn2

#
# print(f"non_expander: {supervisor_query_non_expander("MYC", false_response, 5)}")

def save_results(dict_dict: dict[str, dict], inputs: dict[str, dict] | list[str] = None, ):
  try:
    with open('output.json', 'r') as json_file:
      json_dict = json.load(json_file)
  except FileNotFoundError:
    json_dict = {}
  json_dict.update({k: v for k, v in dict_dict.items() if v})
  with open('output.json', 'w') as json_file:
    json.dump(json_dict, json_file, indent=4)
#   # with open('saved_results.txt', 'a') as file:  # Write the string to the file
#   #     file.write(f"input: {inputs}: \nresults dict_dict: {dict_dict}")
#   #     file.write("\n\n")
#   #     file.close()
#   return dict_dict


def depth_reducer(gene: str, dict_dict: dict[str, Optional[dict]], depth_tree: dict[str, int], starting_depth: int, max_depth: int, network_builder_func: callable, query_func: callable):
  if starting_depth < max_depth:
    depth_tree[gene] = starting_depth
    if dict_dict[gene] is not None:
      for child in dict_dict[gene]:
        if child is None:
          dict_dict.update(network_builder_func(dict_dict, max_depth, depth_tree, starting_depth + 1, query_func))
          depth_tree.update({g: starting_depth + 1 for g in list(dict_dict.keys()) if g not in depth_tree})
        else:
          depth_reducer(child, dict_dict, depth_tree, starting_depth + 1, max_depth, network_builder_func, query_func)
      else:
        dict_dict.update(network_builder_func(dict_dict, max_depth, depth_tree, starting_depth + 1, query_func))
        depth_tree.update({g: starting_depth + 1 for g in list(dict_dict.keys()) if g not in depth_tree})

def network_builder(input_genes: dict[str, Optional[dict]] | list[str], max_depth: int, input_depth_tree: dict[str, int]=None ,current_depth: int = 1, query_func: callable(str) = gene_query_with_format_check):
  print(f"network builder called, depth: {current_depth}")
  if type(input_genes) is list:
    dict_dict: dict[str, Optional[dict]] = {k: None for k in input_genes}
    gene_list = input_genes
    depth_tree = {g: current_depth for g in input_genes}
  else:
    dict_dict: dict[str, Optional[dict]] = input_genes
    gene_list = [key for key, value in input_genes.items() if value is None]
    if input_depth_tree:
      depth_tree = input_depth_tree
    else:
      depth_tree = {g: (current_depth if g in gene_list else 0) for g in input_genes}
  for gene in gene_list:
    if gene not in list(depth_tree.keys()) or depth_tree[gene] == current_depth:
      print(f'processing {gene}, depth: {depth_tree}')
      results_dict = query_func(gene)
      if results_dict:
        dict_dict[gene] = results_dict
        for key in results_dict.keys():
          if key not in dict_dict:
            dict_dict[key] = None  # Not investigated because depth limit was reached
            depth_tree[key] = current_depth + 1
        if  current_depth != max_depth:
          dict_dict.update(network_builder( dict_dict, max_depth, depth_tree, current_depth + 1, query_func))
          depth_tree.update({g: current_depth + 1 for g in list(dict_dict.keys()) if g not in depth_tree})#TODO: I think this is not correct. It sets the depth to currentdepth+1, even if it was from a deeper branch
      else:
        dict_dict[gene] = {}
    elif gene in list(depth_tree.keys()) and depth_tree[gene] > current_depth:
      print(f'depth tree processing {gene}')
      depth_reducer(gene, dict_dict, depth_tree, current_depth, max_depth, network_builder, query_func)
  print(f"depth_tree: {depth_tree}")
  return dict_dict

def matrix_builder(dict_dict: dict[str, dict]):
  # full_set: set[str] = set()
  # for gene in dict_dict:
  #   full_set.add(gene)
  #   full_set.update(set(dict_dict[gene].keys()))

  full_list = list(dict_dict.keys())#list(full_set)
  data = {}
  for gene in full_list:
    if dict_dict[gene] is not None:
      interactions = []
      targets = list(dict_dict[gene].keys())
      for downstream_gene in full_list:
        if downstream_gene not in targets:
          interactions.append(0)
        else:
          interactions.append(dict_dict[gene][downstream_gene])
      data[gene] = interactions
    else:
      data[gene] = ['x' for gene in full_list]
  dataframe = pd.DataFrame(data, index=full_list)
  return dataframe

def cytoscape_visualizer(starting_genes: list[str], dict_dict: dict[str, dict]):
  try:
    # Connect to Cytoscape
    p4c.cytoscape_ping()
    source = []
    target = []
    interaction = []
    interaction_weight = []
    node_type = []
    for gene in list(dict_dict.keys()):
      if dict_dict[gene]:
        node_type.append("TF")
        for target_gene in list(dict_dict[gene].keys()):
          interaction_value = dict_dict[gene][target_gene]
          if interaction_value < 0:
            source.append(gene)
            target.append(target_gene)
            interaction.append('inhibits')
            interaction_weight.append(interaction_value)
          elif interaction_value > 0:
            source.append(gene)
            target.append(target_gene)
            interaction.append('activates')
            interaction_weight.append(interaction_value)
      elif dict_dict[gene] is None:
        node_type.append("?")
      elif dict_dict[gene] == {}:
        node_type.append("end")
    nodes = pd.DataFrame(
      data={'id': list(dict_dict.keys()), 'node_type': node_type, 'is_starter': [1 if x in starting_genes else 0 for x in list(dict_dict.keys())]} )
    edges = pd.DataFrame(
      data={'source': source, 'target': target, 'interaction': interaction, 'interaction_weight': interaction_weight},)

    p4c.create_network_from_data_frames(nodes, edges, title="my first network", collection="DataFrame Example")
    p4c.set_edge_target_arrow_shape_mapping('interaction', ['activates', 'inhibits'], shapes= ['Arrow', 'T'])
    p4c.set_edge_color_mapping('interaction', ['activates', 'inhibits'], colors = ['#000000', '#FF0000'], mapping_type= 'd')
    p4c.set_edge_line_width_mapping('interaction_weight', table_column_values= [-1, 0, 1,], widths=[2, 0, 2])#list(np.arange(-1, 1, 0.1)), widths= list(range(10, 0, -1)) + list(range(1, 11)))
    p4c.set_node_color_mapping('node_type', ["TF", "?", "end"], colors = ['#EFC3CA', '#BFD641', '#98F5F9'], mapping_type= 'd')
    p4c.set_node_border_width_mapping('is_starter', table_column_values= ["1", "0"], widths= [10, 0], mapping_type= 'd',default_width= 1)
    p4c.set_node_border_color_default("#E4080A")

    print("Network with custom edge styles created successfully!")
  except Exception as e:
    print(f"Error: {e}")

def load_results(inputs: dict[str, dict] | list[str], filename: str = 'saved_results.txt'):
  with open(filename, 'r') as file:
    content = file.read()

  # Split the content into sections
  sections = content.split("\n\n")

  for section in sections:
    if f"input: {inputs}:" in section:
      start = section.find("results dict_dict: ") + len("results dict_dict: ")
      dict_str = section[start:]
      dict_dict = ast.literal_eval(dict_str)
      return dict_dict

  return None

def full_workflow(input_genes: list[str], max_depth: int, max_number_of_supervisions: int = 40, generate_cytoscape: bool = True, generate_matrix: bool = True):
  call = network_builder(
      input_genes=input_genes,
      max_depth=max_depth,
      query_func= lambda gene_x: default_query_with_supervisions(gene_x, max_number_of_supervisions)
  )
  if generate_cytoscape:
    cytoscape_visualizer(
      starting_genes=input_genes,
      dict_dict=call
    )
  if generate_matrix:
    matrix_builder(call).to_csv("matrix_output.csv", index=True)

def validator():
  tf_list, test_dict = read_tsv('input/trrust_rawdata.human.tsv')
  test_genes = tf_list.intersection(sven_genes)
  random_20 = random.sample(list(test_genes), 10)

  llm_dict_dict = network_builder(
    input_genes=random_20,
    max_depth=1,
    query_func=lambda gene_x: default_query_with_supervisions(gene_x)
  )
  valid_llm = {k:v for k, v in llm_dict_dict.items() if v is not None}
  converted_llm_dict = {k: list(v.keys())   for k, v in valid_llm.items()}

  for tf in random_20:
    llm_set = set(converted_llm_dict[tf])
    test_set = set(test_dict[tf])
    intersec = test_set.intersection(llm_set)
    only_in_llm = set(converted_llm_dict[tf]) - intersec
    only_in_test = set(test_dict[tf]) - intersec
    # diagram_data.append([tf, only_in_llm, intersec, only_in_test])

    # Create Venn diagram
    venn = venn2((llm_set, test_set), ('LLM', 'TRRUST'))
    if venn.get_label_by_id('10'): venn.get_label_by_id('10').set_text('\n'.join(only_in_llm))
    if venn.get_label_by_id('01'): venn.get_label_by_id('01').set_text('\n'.join(only_in_test))
    if venn.get_label_by_id('11'): venn.get_label_by_id('11').set_text('\n'.join(intersec))
    plt.title(f'Comparison of {tf} Targets')
    plt.show()
#
#Last date: October 21, 2023
#Gene name synonyms

