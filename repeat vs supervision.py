import random

import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import ttest_rel

from get_response import repeated_query, gene_query_with_format_check, default_query_with_supervisions, \
    supervisor_query_expander, results_to_dictionary
from input.input_data import sven_genes

test_gene_list = ["SOX2", "MYC", "FOXO3", "CREB", "OLIG2", "ATF4", "REST", "Ascl1"] + random.sample(sven_genes, 5)

repeated_query_result = {}
supervision_result = {}
for gene in test_gene_list:
    print("Testing " + gene)
    repeated_query_result[gene] = repeated_query(10, gene, gene_query_with_format_check)
    supervision_result[gene] = results_to_dictionary(supervisor_query_expander(gene, gene_query_with_format_check(gene), 9)[0])

print("rep:", repeated_query_result, '\n', "sup:", supervision_result)
# Plot the bar chart
# Extract results as lists
repeated_values = [len(dic) for dic in repeated_query_result.values()]
supervision_values = [len(dic) for dic in supervision_result.values()]

# Plot the bar chart
x = np.arange(len(test_gene_list))  # Gene indices
width = 0.35  # Width of each bar

fig, ax = plt.subplots(figsize=(10, 6))

# Create bars for each parameter
ax.bar(x - width / 2, repeated_values, width, label='Repeated Query')
ax.bar(x + width / 2, supervision_values, width, label='Supervision Query')

# Add labels, title, and legend
ax.set_xlabel('Genes')
ax.set_ylabel('Average Number of Targets')
ax.set_title('Comparison of Query Methods for Test Genes')
ax.set_xticks(x)
ax.set_xticklabels(test_gene_list, rotation=45, ha='right')
ax.legend()

# Display the plot
plt.tight_layout()
plt.show()

print("T-test Results:")
print("rep:", repeated_values, '\n', "sup:", supervision_values)
t_stat, p_value = ttest_rel(repeated_values, supervision_values)
print(f"rep vs sup: t-statistic = {t_stat:.2f}, p-value = {p_value:.4f}")
