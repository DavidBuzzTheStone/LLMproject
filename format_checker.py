
import re

def clean_string_from_unwanted_characters(input_str: str):
  return input_str.replace(",", "").replace("\n", "").replace("]", "").replace("[", "")


def check_format(input_string: str, on_wrong: callable):
  # Define the regex pattern for the correct format
  pattern = r"^(stimulates: (none|[A-Z0-9 ]+)(, )?\n?inhibits: (none|[A-Z0-9 ]+)|none)$"
  cleaned_input = clean_string_from_unwanted_characters(input_string)
  # Check if the input string matches the pattern
  if re.match(pattern, cleaned_input):
    return cleaned_input
  else:
    print(f"Format is incorrect: {input_string}")
    if on_wrong:
        return on_wrong
    else: print("Incorrect format 3 times in a row")