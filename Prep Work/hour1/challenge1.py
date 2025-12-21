import spacy 

nlp = spacy.load("en_core_web_sm")

text = "SpaCy is an amazing library for Natural Language Processing!"

doc = nlp(text)

for token in doc:
    print(f"{token.text} | {token.lemma_} | {token.pos_} | {token.tag_} | {token.is_stop}")
