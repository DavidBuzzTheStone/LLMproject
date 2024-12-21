import random

from format_checker import clean_string_from_unwanted_characters, check_format
from get_response import get_response, results_to_dictionary
from input.input_data import sven_genes
import matplotlib.pyplot as plt
import numpy as np

from scipy.stats import f_oneway
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scipy.stats import ttest_ind


test_gene_list = ["SOX2", "MYC", "TGF-β", "FOXO3"] + random.sample((sven_genes), 6)

def test_message_list(test_gene:str):
    return  [
    f"""List all known downstream targets of {test_gene} in Homo sapiens (human), specifically in brain tissue.
    Provide the results in this exact format:
    
    Stimulates: [gene1; gene2; gene3]
    Inhibits: [gene4; gene5; gene6]
    If no downstream targets are known, respond with "none" for both categories.
    Do not provide additional information or commentary.""",

    f"""
      List all known downstream targets of {test_gene}.
      Organism: homo sapiens. Tissue: brain.
      Use the following format: "stimulates: [gene names], inhibits: [gene names]" with the gene names separated by ';'.
      If there is no downstream target, answer "none". 
      Don't say anything else.
    """,

    "Molecular Biology Expert and Educator",
    "Genomics Research Supervisor",
    "Expert Reviewer in Molecular and Brain Genomics",
    "Senior Scientist in Human Brain Genomics",
    "Teaching Assistant in Genomics and Molecular Biology",
    ]


test_results = {}
full_test_results = {}
for tested_parameter in tested_parameters2:
    print("Testing", tested_parameter)
    parameter_result_dic = {}
    full_parameter_result_dic = {}
    for test_gene in test_gene_list:
        average_number_of_test_gene_targets = 0
        full_results = []
        number_of_repeats = 4
        for i in range(number_of_repeats):
             full_results.append(results_to_dictionary(
                check_format(
                get_response(
                    role="You are an expert in molecular biology and genomics of human brain",
                    prompt = f"""
                  List all known downstream targets of {test_gene}.
                  Organism: homo sapiens. Tissue: brain.
                  Use the following format: "stimulates: [gene names], inhibits: [gene names]" with the gene names separated by ';'.
                  If there is no downstream target, answer "none". 
                  Don't say anything else.
                """,
                    model = "chatgpt-4o-latest",
                    temperature=0.05,
                    top_p=1,
                    frequency_penalty=tested_parameter
                  ), None
                )
             )
             )
             average_number_of_test_gene_targets += len(full_results[i])
        average_number_of_test_gene_targets /= number_of_repeats
        parameter_result_dic[test_gene] = average_number_of_test_gene_targets
        full_parameter_result_dic[test_gene] = full_results
    test_results[tested_parameter] = parameter_result_dic
    full_test_results[tested_parameter] = full_parameter_result_dic
for parameter in test_results:
    print(parameter, test_results[parameter])
    print(parameter, full_test_results[parameter])

# Extract genes and parameters
genes = list(next(iter(test_results.values())).keys())
parameters = list(test_results.keys())

# Prepare data for plotting
average_targets = {
    parameter: [test_results[parameter][gene] for gene in genes]
    for parameter in parameters
}

# Plot the bar chart
x = np.arange(len(genes))  * (1 + 0.2)# Gene indices + padding
width = 0.15  # Width of each bar

fig, ax = plt.subplots(figsize=(14, 6))

# Create bars for each parameter
for i, parameter in enumerate(parameters):
    ax.bar(x + i * width, average_targets[parameter], width, label=parameter)

# Add labels, title, and legend
ax.set_xlabel('Genes')
ax.set_ylabel('Average Number of Targets')
ax.set_title('Average Number of Test Gene Targets by Parameter')
ax.set_xticks(x + width * (len(parameters) - 1) / 2)
ax.set_xticklabels(genes)
ax.legend()

# Display the plot
plt.tight_layout()
plt.show()

# Prepare data for statistical tests
all_data = []
all_labels = []
for parameter, values in average_targets.items():
    all_data.extend(values)
    all_labels.extend([parameter] * len(values))

# Perform Repeated Measures ANOVA
anova_stat, anova_p_value = f_oneway(*[average_targets[param] for param in parameters])
print(f"ANOVA Results: F-statistic = {anova_stat:.2f}, p-value = {anova_p_value:.4f}")

# Perform Tukey's HSD test if ANOVA is significant
if anova_p_value < 0.05:
    print("Post-hoc Tukey's HSD Test:")
    tukey_result = pairwise_tukeyhsd(endog=all_data, groups=all_labels, alpha=0.05)
    print(tukey_result)
else:
    print("No significant differences found; skipping Tukey's HSD test.")
