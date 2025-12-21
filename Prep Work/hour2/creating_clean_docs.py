import spacy
from spacy.language import Language
from spacy.tokens import Doc

def clean_doc(doc):
    cleaned_tokens = []
    flag = False
    for token in doc:
        if flag: 
            flag = False
        elif token.text == "#":
            flag = True
        elif not (token.is_stop or token.is_punct or token.is_space or token.like_num or token.like_url or token.like_email or token.text.startswith("@") or token.text.startswith("#")):
            cleaned_tokens.append(token.lower_)
    return cleaned_tokens

@Language.component("custom_cleaner")
def custom_cleaner(doc):
    cleaned_tokens = clean_doc(doc)
    doc._.cleaned_tokens = cleaned_tokens
    doc._.cleaned_doc = nlp(" ".join(cleaned_tokens))
    return doc

nlp = spacy.load("en_core_web_sm")

from spacy.tokens import Doc

if not Doc.has_extension("cleaned_tokens"):
    Doc.set_extension("cleaned_tokens", default=[])

if not Doc.has_extension("cleaned_doc"):
    Doc.set_extension("cleaned_doc")

nlp.add_pipe("custom_cleaner", last=True)

text = "Follow @OpenAI and use #AI for the latest updates. Visit https://openai.com or email info@openai.com!"
doc = nlp(text)



