with open("input/sven_tf_list.txt", 'r') as file:
    content = file.read()
    sven_genes = content.split('\n')

with open("input/TF_names_v_1.01.txt", 'r') as file:
    content = file.read()
    full_tf_list = content.split('\n')
