
import re
import sys
from logging import exception

def remove_parentheses(text): return re.sub(r'\(.*?\)', '', text)

def clean_string_from_unwanted_characters(input_str: str):
  return input_str.replace(",", "").replace("; ", ";").replace("\n", "").replace("]", "").replace("[", "").replace("None", "none").replace("NONE", "none")


def check_format(input_string: str, on_wrong: callable):
  cleaned_input = clean_string_from_unwanted_characters(remove_parentheses(input_string))
  # Define the regex pattern for the correct format
  missing_inh_pattern = r"^(stimulates:\s*(none|[A-Za-z0-9\u0370-\u03FF\- ;]+)\s*)$"
  missing_stim_pattern = r"^(inhibits:\s*(none|[A-Za-z0-9\u0370-\u03FF\- ;]+)\s*)$"
  reversed_pattern = r"^(inhibits:\s*(none|[A-Za-z0-9\u0370-\u03FF\- ;]+)|none)\s*stimulates:\s*(none|[A-Za-z0-9\u0370-\u03FF\- ;]+)$"
  if re.match(missing_inh_pattern, cleaned_input):
    cleaned_input += "inhibits: none"
  if re.match(missing_stim_pattern, cleaned_input):
    cleaned_input = "stimulates: none " + cleaned_input
  if re.match(reversed_pattern, cleaned_input):
    parts = cleaned_input.split("stimulates:")
    cleaned_input = f"stimulates:{parts[1]} {parts[0]}"
  pattern = r"^(stimulates:\s*(none|[A-Za-z0-9\u0370-\u03FF\- ;]+)\s*inhibits:\s*(none|[A-Za-z0-9\u0370-\u03FF\- ;]+)\s*|none\s*)$"
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
# check_format("stimulates: PPAR γ ", None)
thing = "stimulates: BDNF; FOS; JUN; NR4A1; NR4A2; NR4A3; EGR1; EGR2; EGR3; ARC; DUSP1; NPTX2; CEBPB; PER1; PER2; PER3; CREM; IRS2; PGC1A; SYN1; SYN2; SYN3; CAMK4; VGF; NTRK2; GRIA1; GRIA2; GRIN1; GRIN2A; GRIN2B; SLC2A3; SLC2A4; SLC6A4; SLC12A5; PPP1R1B; RGS2; RGS4; RGS14; KLF4; KLF15; ATF3; ATF4; ATF5; GADD45B; GADD45G; HOMER1; HOMER2; HOMER3; CRTC1; CRTC2; CRTC3; PIK3CA; PIK3CB; PIK3CD; PIK3R1; PIK3R2; PIK3R3; AKT1; AKT2; AKT3; MTOR; MAPK1; MAPK3; MAPK8; MAPK9; MAPK10; MAPK14; DLG4; SHANK1; SHANK2; SHANK3; PSD95; PSD93; SYNPO; SYNPO2; SYNPO3; NLGN1; NLGN2; NLGN3; NLGN4; NRXN1; NRXN2; NRXN3; GABRA1; GABRA2; GABRA3; GABRA4; GABRA5; GABRB1; GABRB2; GABRB3; GABRG1; GABRG2; GABRG3; GABRD; GABRE; GABRP; GABRQ; GABRR1; GABRR2; GABRR3; SYP; SNAP25; STX1A; STX1B; STXBP1; STXBP2; STXBP3; STXBP4; STXBP5; STXBP6; SYT1; SYT2; SYT3; SYT4; SYT5; SYT6; SYT7; SYT8; SYT9; SYT10; SYT11; SYT12; SYT13; SYT14; SYT15; SYT16; SYT17; SYT18; SYT19; SYT20; SYT21; SYT22; SYT23; SYT24; SYT25; SYT26; SYT27; SYT28; SYT29; SYT30; SYT31; SYT32; SYT33; SYT34; SYT35; SYT36; SYT37; SYT38; SYT39; SYT40; SYT41; SYT42; SYT43; SYT44; SYT45; SYT46; SYT47; SYT48; SYT49; SYT50; SYT51; SYT52; SYT53; SYT54; SYT55; SYT56; SYT57; SYT58; SYT59; SYT60; SYT61; SYT62; SYT63; SYT64; SYT65; SYT66; SYT67; SYT68; SYT69; SYT70; SYT71; SYT72; SYT73; SYT74; SYT75; SYT76; SYT77; SYT78; SYT79; SYT80; SYT81; SYT82; SYT83; SYT84; SYT85; SYT86; SYT87; SYT88; SYT89; SYT90; SYT91; SYT92; SYT93; SYT94; SYT95; SYT96; SYT97; SYT98; SYT99; SYT100; SYT101; SYT102; SYT103; SYT104; SYT105; SYT106; SYT107; SYT108; SYT109; SYT110; SYT111; SYT112; SYT113; SYT114; SYT115; SYT116; SYT117; SYT118; SYT119; SYT120; SYT121; SYT122; SYT123; SYT124; SYT125; SYT126; SYT127; SYT128; SYT129; SYT"
print(check_format(thing, None) )