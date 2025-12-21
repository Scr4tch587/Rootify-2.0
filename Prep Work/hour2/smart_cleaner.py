import spacy
from spacy.language import Language
from spacy.tokens import Doc

def filter_doc(doc):
    filtered_tokens = []
    flag = False
    for token in doc:
        if token.pos_ in {'NOUN', 'PRON', 'ADJ'}:
            filtered_tokens.append(token.lower_)
    return filtered_tokens

@Language.component("summary_prep")
def summary_prep(doc):
    filtered_tokens = filter_doc(doc)
    doc._.summary_tokens = filtered_tokens
    doc._.summary_doc = nlp.make_doc(" ".join(filtered_tokens))
    freq_dict = {}
    for token in filtered_tokens:
        if token in freq_dict:
            freq_dict[token] += 1
        else:
            freq_dict[token] = 1
    freq_dict = dict(sorted(freq_dict.items(), key=lambda item: item[1], reverse=True))
    doc._.summary_freq = freq_dict
    return doc

nlp = spacy.load("en_core_web_sm")
from spacy.tokens import Doc

if not Doc.has_extension("summary_tokens"):
    Doc.set_extension("summary_tokens", default=[])

if not Doc.has_extension("summary_doc"):
    Doc.set_extension("summary_doc", default=None)

if not Doc.has_extension("summary_freq"):
    Doc.set_extension("summary_freq", default={})

nlp.add_pipe("summary_prep", last=True)

text = "Artificial intelligence is transforming industries worldwide. Many companies invest heavily in AI research and development. Innovative applications of machine learning and natural language processing are driving this change. However, ethical considerations and data privacy remain important challenges."
doc = nlp(text)

print(doc._.summary_tokens)
counter = 0
for key in doc._.summary_freq:
    counter += 1
    print(f"{key}: {doc._.summary_freq[key]}")
    if counter == 5: break