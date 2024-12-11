from openai import OpenAI, default_query

from format_checker import check_format

api_key = "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"
client = OpenAI(api_key=api_key)

def get_response(
        role: str,
        prompt: str, model: str = "chatgpt-4o-latest", temperature: float = 0.05, max_tokens: int = 500, top_p: float = 1,):
  response = client.chat.completions.create(
    model=model,
    messages=[
      {
        "role": "system",
        "content": f""" {role} """
      },
      {
        "role": "user",
        "content": f"""{prompt} """
      }
      ],
        temperature= temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=0,
        presence_penalty=0
    )
  return response.choices[0].message.content

def results_to_dictionary(results: str):
  print(results)
  dictionary = {}
  if results == "none":
    return dictionary
  else:
    split_results = results.split("inhibits:")
    activated_targets = split_results[0].removeprefix("stimulates:").split(" ")
    inhibited_targets = split_results[1].split(" ")

    for inhibited_target in inhibited_targets:
      if inhibited_target not in dictionary and inhibited_target != '' and inhibited_target != "none":
        dictionary[inhibited_target.upper()] = -1

    for activated_target in activated_targets:
      if activated_target not in dictionary and activated_target != '' and activated_target != "none":
        dictionary[activated_target.upper()] = 1
    return dictionary


def supervisor_call(gene_name: str, response: str):
  return get_response(
    role=f"""
      You are an expert in molecular biology and genomics of human brain. 
      You will supervise the responses given by students to this prompt:

      '''List all known downstream targets of {gene_name}.
      Organism: homo sapiens. Tissue: brain.
      Use the following format: "stimulates: [gene names], inhibits: [gene names]" separated by spaces.
      If there is no downstream target, answer "none". 
      Don't say anything else.'''

      Provide your response in a similar format, completing the student's answer with every target that the student missed.
      Don't say anything besides the correct answer.
      """,

    prompt=f"""
      response given by student: {response} 
    """,
    model="chatgpt-4o-latest",
  )


def supervisor_query_expander(gene_name: str, response: str, number_of_supervisions: int = 1):
   if number_of_supervisions > 1:
     new_response = supervisor_query_expander(gene_name, response, number_of_supervisions-1)
   else:
     new_response = response

   return check_format(
     input_string=supervisor_call(gene_name, new_response),
     on_wrong= check_format(
       input_string=supervisor_call(gene_name, new_response),
       on_wrong =check_format(
         input_string=supervisor_call(gene_name, new_response),
         on_wrong=None
       )
     )
   )


# def response_binder(resp1: str, resp2: str):
#   resp1_list = resp1.replace(",","").replace("none", "").removeprefix("stimulates: ").split("inhibits: ")
#   resp2_list = resp2.replace(",", "").replace("none", "").removeprefix("stimulates: ").split("inhibits: ")
#   if (resp1_list[0] + resp2_list[0]).replace(" ", "") == "":
#     new_stim = "none"
#   else:
#     new_stim = (resp1_list[0] + resp2_list[0])
#
#   if (resp1_list[1] + resp2_list[1]).replace(" ", "") == "":
#     new_inh = "none"
#   else:
#     new_inh = (resp1_list[1] + resp2_list[1])
#   return f"stimulates: {new_stim}, inhibits: {new_inh}".replace("\n", " ").replace("  ", " ").replace(" , ", ",")
#
# def supervisor_query_non_expander(gene_name: str, response: str, number_of_supervisions: int = 1):
#
#   if number_of_supervisions > 1:
#     new_response = supervisor_query_non_expander(gene_name, response, number_of_supervisions - 1)
#   else:
#     new_response = response
#
#
#   return response_binder(get_response(
#       role=f"""
#       You are an expert in molecular biology and genomics of human brain.
#       You will supervise the responses given by students to this prompt:
#
#       '''List all known downstream targets of {gene_name}.
#       Organism: homo sapiens. Tissue: brain.
#       Use the following format: "stimulates: [gene names], inhibits: [gene names]" separated by spaces.
#       If there is no downstream target, answer "none".
#       Don't say anything else.'''
#
#       Provide your response in a similar format, listing every target that the student missed.
#       """,
#       prompt=f"""
#       response given by student: {new_response}
#     """,
#       model="chatgpt-4o-latest",
#     ), new_response)
#
#

# def repeated_results_to_dictionary(results: str):
#   if results == "none":
#     return [], []
#   else:
#     split_results = clean_string_from_unwanted_characters(results).split("inhibits:")
#     activated_targets = split_results[0].removeprefix("stimulates:").split(" ")
#     inhibited_targets = split_results[1].split(" ")
#   return activated_targets, inhibited_targets
#
#
# def repeated_query(number_of_repeats: int, gene: str, query_func: callable(str)):
#   stimulates = []
#   inhibits = []
#   dictionary = {}
#   for _ in range(number_of_repeats):
#
#     new_activated, new_inhibited = repeated_results_to_dictionary(query_func(gene))
#     stimulates += new_activated
#     inhibits += new_inhibited
#   stimulates = [x for x in stimulates if x != "none" and x != ""]
#   inhibits = [x for x in inhibits if x != "none" and x != ""]
#   all_genes = set(stimulates).union(set(inhibits))
#   for gene in all_genes:
#     value = (stimulates.count(gene) - inhibits.count(gene))/number_of_repeats
#     dictionary[gene] = value
#   return dictionary

# A different approach would be simply combining all the responses into a list, or returning this list to ChatGPT to supervise it
