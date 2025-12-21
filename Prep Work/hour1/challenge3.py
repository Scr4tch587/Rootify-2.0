import spacy

nlp = spacy.load("en_core_web_sm")

text = "He was running and eating when I arrived."

doc = nlp(text)

for token in doc:
    if token.pos_ in {"VERB", "AUX"}:
        print(token.lemma_)