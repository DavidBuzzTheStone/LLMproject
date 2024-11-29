
models = ["chatgpt-4o-latest", "gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
temperatures = [0, 0.1, 0.2, 0.3, 0.4, 0.5]
roles = [
    "you are a helpful assistant",
    "you are an expert in molecular biology",
    "You are a molecular biology and genomics expert specialized in human gene regulation.",
    "you are a dog"
]

def test_response(gene_name):
    print("Testing " + gene_name)
    dummy_network = {
        "I1": {"stimulates": ["II1", "II3"], "inhibits": []},
        "I2": {"stimulates": ["II1", "III1"], "inhibits": ["II2"]},
        "II1": {"stimulates": ["III1"], "inhibits": ["II2"]},
        "II2": {"stimulates": ["III2", "III4"], "inhibits": ["III3"]},
        "II3": {"stimulates": ["III3"], "inhibits": []},
        "III1": {"stimulates": [], "inhibits": []},
        "III2": {"stimulates": [], "inhibits": ["I1"]},
        "III3": {"stimulates": ["IV1"], "inhibits": ["III4"]},
        "III4": {"stimulates": [], "inhibits": []},
        "IV1": {"stimulates": [], "inhibits": ["III1"]},
    }

    # Get downstream targets
    if gene_name in dummy_network:
        stimulates = " ".join(dummy_network[gene_name]["stimulates"]) or "none"
        inhibits = " ".join(dummy_network[gene_name]["inhibits"]) or "none"
        return f"stimulates: {stimulates}, inhibits: {inhibits}"
    else:
        print(f"Unknown gene name: {gene_name}")


expected_test_results = (
    {'I1': {'II1': 1, 'II3': 1}, 'II1': {'II2': -1, 'III1': 1}, 'II2': {'III3': -1, 'III2': 1, 'III4': 1}, 'III3': {'III4': -1, 'IV1': 1}, 'III4': {}, 'IV1': {'III1': -1}, 'III1': {}, 'III2': {'I1': -1}, 'II3': {'III3': 1}, 'I2': {'II2': -1, 'II1': 1, 'III1': 1}}
)

