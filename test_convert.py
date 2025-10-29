import unicodedata

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

text = "Thiết bị y tế"
converted = remove_accents(text).lower().replace(" ", "_")
print(converted)  # 👉 an_a
