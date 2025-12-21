import spacy 
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_sm")

text = "Benjamin Fernando Barajas Lasky (born October 2, 2000), better known by his stage name Quadeca (formerly QuadecaX8), is an American singer, songwriter, rapper and record producer. Lasky began on the Internet by uploading rap songs, music videos, comedy sketches, and video game gameplay to his YouTube channel. Quadeca deviated away from his YouTube career to focus on his music career, releasing four mixtapes prior to the albums Voice Memos in 2019, From Me to You in 2021, I Didn't Mean to Haunt You in 2022, and Vanisher, Horizon Scraper in 2025. The mixtape Scrapyard, released on February 16, 2024, contains features from Brakence and Kevin Abstract. His fourth studio album, Vanisher, Horizon Scraper, was released in July 2025, and contains features from Danny Brown, Maruja and Olēka."

doc = nlp(text)

matcher = Matcher(nlp.vocab)
pattern = [
    {"LOWER": "mixtape"},
    {"LOWER": {"NOT_IN": ["released"]}, "IS_PUNCT": False, "OP": "+"},
    {"IS_PUNCT": True, "OP": "*"},
    {"LOWER": "released"},
    {"LOWER": "on"},
]

matcher.add("MIXTAPE_RELEASE", [pattern])

matches = matcher(doc)

for _, start, end in matches:
    i = start
    title_start = i + 1
    j = title_start
    while j < len(doc) and not doc[j].is_punct and doc[j].lower_ != "released":
        j += 1
    title = doc[title_start:j].text

    k = j
    while k < len(doc) and doc[k].lower_ != "on":
        k += 1
    date_window = doc[k:min(k+15, len(doc))]

    date = None
    for ent in date_window.ents:
        if ent.label == "DATE":
            date = ent.text
            break
    if date is None:
        d = k + 1
        while d < len(doc):
            if doc[d].is_punct:
                if doc[d].text == "," and d + 1 < len(doc) and doc[d+1].like_num and len(doc[d+1].text) == 4:
                    d += 1
                    continue
                break
            d += 1
        date = doc[k+1:d].text
    print(title, date)