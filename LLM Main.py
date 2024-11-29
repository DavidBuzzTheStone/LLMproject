from get_response import get_response, api_key, results_to_dictionary, repeated_query
import pandas as pd
import py4cytoscape as p4c
import numpy as np
from typing import Dict, Optional


from test_data import test_response, expected_test_results

def default_gene_query(gene_name: str):
  return get_response(
    role="You are an expert in molecular biology and genomics of human brain",
    prompt = f"""
  List all known downstream targets of {gene_name}.
  Organism: homo sapiens. Tissue: brain.
  Use the following format: "stimulates: [gene names], inhibits: [gene names]" separated by spaces.
  If there is no downstream target, answer "none". 
  Don't say anything else.
""",
    model = "chatgpt-4o-latest",
  )

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

def network_builder(input_genes: dict[str, Optional[dict]] | list[str], max_depth: int, input_depth_tree: dict[str, int]=None ,current_depth: int = 1, query_func: callable(str) = default_gene_query):
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
      response = query_func(gene)
      if type(response) is dict:
        results_dict = response
      else:
        results_dict = results_to_dictionary(query_func(gene))
      if results_dict:
        dict_dict[gene] = results_dict
        for key in results_dict.keys():
          if key not in dict_dict:
            dict_dict[key] = None  # Not investigated because depth limit was reached
            depth_tree[gene] = depth_tree.get(gene, current_depth + 1)
        if  current_depth != max_depth:
          dict_dict.update(network_builder( dict_dict, max_depth, depth_tree, current_depth + 1, query_func))
          depth_tree.update({g: current_depth + 1 for g in list(dict_dict.keys()) if g not in depth_tree})
      else:
        dict_dict[gene] = {}
    elif gene in list(depth_tree.keys()) and depth_tree[gene] > current_depth:
      depth_reducer(gene, dict_dict, depth_tree, current_depth, max_depth, network_builder, query_func)
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

def cytoscape_visualizer(dict_dict: dict[str, dict]):
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
      data={'id': list(dict_dict.keys()), 'node_type': node_type}, )
    edges = pd.DataFrame(
      data={'source': source, 'target': target, 'interaction': interaction, 'interaction_weight': interaction_weight},)

    p4c.create_network_from_data_frames(nodes, edges, title="my first network", collection="DataFrame Example")
    p4c.set_edge_target_arrow_shape_mapping('interaction', ['activates', 'inhibits'], shapes= ['Arrow', 'T'])
    p4c.set_edge_color_mapping('interaction', ['activates', 'inhibits'], colors = ['#000000', '#FF0000'], mapping_type= 'd')
    p4c.set_edge_line_width_mapping('interaction_weight', table_column_values= list(np.arange(-1, 1, 0.1)), widths= list(range(10, 0, -1)) + list(range(1, 11)))
    p4c.set_node_color_mapping('node_type', ["TF", "?", "end"], colors = ['#FF0000', '#00FF00', '#0000FF'], mapping_type= 'd')

    print("Network with custom edge styles created successfully!")
  except Exception as e:
    print(f"Error: {e}")

def save_results(inputs: dict[str, dict] | list[str], dict_dict: dict[str, dict]):
  with open('saved_results.txt', 'a') as file:  # Write the string to the file
      file.write(f"input: {inputs}: \nresults dict_dict: {dict_dict}")
      file.write("\n\n")
      file.close()
  return dict_dict

### TEST
# for i in range(2, 5):
#   #cytoscape_visualizer(network_builder(default_gene_query()))
#   test_call = network_builder(["I1","I2"], set(), i, query_func= test_response)
#print(expected_test_results == test_call)

#matrix_builder(test_call).to_csv("matrix_output.csv", index=True)
#test_call = network_builder(["I1", "I2"], 3, query_func=test_response)
#cytoscape_visualizer(test_call)

#print("test3:")
#test_call3 = network_builder(["I1", "I2"], 4, query_func=test_response)

#new_genes = [k for k, v in test_call.items() if v is None]
#print("test continues:")
#test_call.update(network_builder(test_call, 3, query_func=test_response))
#print(test_call)
#print(test_call3)
#print(test_call3 == test_call)
#print(matrix_builder(test_call))
#Do we need a limit in the AI query function? To prevent endless loops because of hallucination.
#Repeated queries give different answers. Combining/supervising?

#gene = input("Gene: ")
# test_genes = ["sox2"]#["sox2", "sox9", "myc", "tgf beta", "rb"]
#
# with open('repeated_query_cache.txt', 'a') as file: # Write the string to the file
#   for gene in test_genes:
#     for i in range(1, 5):
#        file.write(f"{gene.upper()}: \n")
#        result = default_gene_query(gene)
#        file.write(f"{result}\n")
#   file.write("\n\n")
#
input_genes = ["sox2", "NANOG"]
cytoscape_visualizer(
  save_results(input_genes, network_builder( input_genes, 1, query_func=lambda gene: repeated_query(number_of_repeats=10, gene=gene, query_func=default_gene_query) ))
)
