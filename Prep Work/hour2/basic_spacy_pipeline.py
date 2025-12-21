import spacy
from spacy.language import Language

def clean_doc(doc):
    cleaned_tokens = []
    for token in doc:
        if not (token.is_stop or token.is_punct or token.is_space or token.like_num):
            cleaned_tokens.append(token.lower_)
    return cleaned_tokens

@Language.component("custom_cleaner")
def custom_cleaner(doc):
    cleaned_tokens = clean_doc(doc)
    doc._.cleaned_tokens = cleaned_tokens
    return doc

nlp = spacy.load("en_core_web_sm")

from spacy.tokens import Doc

if not Doc.has_extension("cleaned_tokens"):
    Doc.set_extension("cleaned_tokens", default=[])

nlp.add_pipe("custom_cleaner", last=True)

doc = nlp("This is an example! There are 100 tokens, and some stopwards to remove.")
print(doc._.cleaned_tokens)
