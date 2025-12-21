import spacy

nlp = spacy.load("en_core_web_sm")

def makeEntityDict(doc):
    entity_dict = {}
    ent_labels = set()
    for ent in doc.ents:
        ent_labels.add(ent.label_)
    for label in ent_labels:
        entity_dict[label] = []
    for ent in doc.ents:
        if ent.label_ in entity_dict:
            entity_dict[ent.label_].append(ent.text)

    return entity_dict


text = "Apple is planning to buy a startup in London for $1 billion."

doc = nlp(text)

entity_dict = makeEntityDict(doc)
print(entity_dict)