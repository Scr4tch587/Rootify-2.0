import spacy

nlp = spacy.load("en_core_web_sm")

text = "The quick brown fox jumps over the lazy dog"

doc = nlp(text)

for token in doc:
    if token.pos_ == "ADJ":
        if token.dep_ == "amod":
            print(f"{token.text} -> {token.head.text}")