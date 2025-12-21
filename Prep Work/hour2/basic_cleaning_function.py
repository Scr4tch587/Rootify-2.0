import spacy
nlp = spacy.load("en_core_web_sm")

def clean_doc(doc):
    cleaned_tokens = []
    for token in doc:
        if not (token.is_stop or token.is_punct or token.is_space or token.like_num):
            cleaned_tokens.append(token.lower_)
    return cleaned_tokens

text = "This is an example! There are 100 tokens, and some stopwords to remove."

doc = nlp(text)

print(clean_doc(doc))
