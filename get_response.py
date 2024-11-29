from openai import OpenAI, default_query

api_key = "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"
client = OpenAI(api_key=api_key)

def get_response(role: str, prompt: str, model: str = "gpt-4o-latest", temperature: float = 0.05, max_tokens: int = 500, top_p: float = 1,):
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

def clean_string_from_unwanted_characters(input_str: str):
  return input_str.replace(",", "").replace("\n", "").replace("]", "").replace("[", "")


def results_to_dictionary(results: str):
  dictionary = {}
  if results == "none":
    return dictionary
  else:
    split_results = clean_string_from_unwanted_characters(results).split("inhibits:")
    activated_targets = split_results[0].removeprefix("stimulates:").split(" ")
    inhibited_targets = split_results[1].split(" ")

    for inhibited_target in inhibited_targets:
      if inhibited_target not in dictionary and inhibited_target != '' and inhibited_target != "none":
        dictionary[inhibited_target] = -1

    for activated_target in activated_targets:
      if activated_target not in dictionary and activated_target != '' and activated_target != "none":
        dictionary[activated_target] = 1
    return dictionary

def repeated_results_to_dictionary(results: str):
  if results == "none":
    return [], []
  else:
    split_results = clean_string_from_unwanted_characters(results).split("inhibits:")
    activated_targets = split_results[0].removeprefix("stimulates:").split(" ")
    inhibited_targets = split_results[1].split(" ")
  return activated_targets, inhibited_targets


def repeated_query(number_of_repeats: int, gene: str, query_func: callable(str)):
  stimulates = []
  inhibits = []
  dictionary = {}
  for _ in range(number_of_repeats):

    new_activated, new_inhibited = repeated_results_to_dictionary(query_func(gene))
    stimulates += new_activated
    inhibits += new_inhibited
  stimulates = [x for x in stimulates if x != "none" and x != ""]
  inhibits = [x for x in inhibits if x != "none" and x != ""]
  all_genes = set(stimulates).union(set(inhibits))
  for gene in all_genes:
    value = (stimulates.count(gene) - inhibits.count(gene))/number_of_repeats
    dictionary[gene] = value
  return dictionary

