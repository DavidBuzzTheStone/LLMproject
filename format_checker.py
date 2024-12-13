
import re
import sys
from logging import exception

from numpy.f2py.auxfuncs import throw_error


def clean_string_from_unwanted_characters(input_str: str):
  return input_str.replace(",", "").replace("; ", ";").replace("\n", "").replace("]", "").replace("[", "")


def check_format(input_string: str, on_wrong: callable):
  cleaned_input = clean_string_from_unwanted_characters(input_string)
  # Define the regex pattern for the correct format
  missing_inh_pattern = r"^(stimulates:\s*(none|[A-Za-z0-9\u0370-\u03FF\-;]+)\s*)$"
  missing_stim_pattern = r"^(inhibits:\s*(none|[A-Za-z0-9\u0370-\u03FF\-;]+)\s*)$"
  reversed_pattern = r"^(inhibits:\s*(none|[A-Za-z0-9\u0370-\u03FF\-;]+)|none)\s*stimulates:\s*(none|[A-Za-z0-9\u0370-\u03FF\- ]+)$"
  if re.match(missing_inh_pattern, cleaned_input):
    cleaned_input += "inhibits: none"
  if re.match(missing_stim_pattern, cleaned_input):
    cleaned_input = "stimulates: none " + cleaned_input
  if re.match(reversed_pattern, cleaned_input):
    parts = cleaned_input.split("stimulates:")
    cleaned_input = f"stimulates:{parts[1]} {parts[0]}"
  pattern = r"^(stimulates:\s*(none|[A-Za-z0-9\u0370-\u03FF\-;]+)\s*inhibits:\s*(none|[A-Za-z0-9\u0370-\u03FF\-;]+)\s*|none\s*)$"
  # Check if the input string matches the pattern
  if re.match(pattern, cleaned_input):
    print(f"Formatting OK - {cleaned_input}")
    return cleaned_input
  else:
    print(f"Format is incorrect: {input_string}, cleaned input: {cleaned_input}")
    if on_wrong is not None:
        return on_wrong()
    else:
      exception("Incorrect format 3 times in a row")
      sys.exit(1)

# check_format("stimulates: NDEL1 inhibits: AXIN1 CTNNB1 TSC2 APC MAPT NFATC1 MCL1 PTEN JUN EIF2B5 CREB1 BCL2 SMAD1 SMAD3 SHC1 SNAI1 GLI3 CCND1 MYC PER2 TAU β-CATENIN", None)
# check_format("none", None)
# check_format("stimulates: PPARγ ", None)
