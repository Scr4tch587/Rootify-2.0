import spacy 

nlp = spacy.load("en_core_web_sm")

text = "Apple is looking at buying U.K. startup for $1 billion"

doc = nlp(text)

print("Tokens:")
for token in doc:
    print(f"(token.text) (lemma:{token.lemma_})")

print("\nPart-of-Speech Tags:")
for token in doc:
    print(f"{token.text} (lemma: {token.dep_})")

print("\nNamed Entities:")
for ent in doc.ents:
    print(f"{ent.text} ({ent.label_})")

for token in doc:
    print(f"{token.text} <--{token.dep_}-- {token.head.text}")
