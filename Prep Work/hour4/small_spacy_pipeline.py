import pandas as pd
import spacy

text1 = "Benjamin Fernando Barajas Lasky (born October 2, 2000), better known by his stage name Quadeca (formerly QuadecaX8), is an American singer, songwriter, rapper and record producer. Lasky began on the Internet by uploading rap songs, music videos, comedy sketches, and video game gameplay to his YouTube channel. Quadeca deviated away from his YouTube career to focus on his music career, releasing four mixtapes prior to the albums Voice Memos in 2019, From Me to You in 2021, I Didn't Mean to Haunt You in 2022, and Vanisher, Horizon Scraper in 2025. The mixtape Scrapyard, released on February 16, 2024, contains features from Brakence and Kevin Abstract. His fourth studio album, Vanisher, Horizon Scraper, was released in July 2025, and contains features from Danny Brown, Maruja and Olēka."
text2 = "Noel Scott Engel (January 9, 1943 - March 22, 2019),[1] better known by his stage name Scott Walker, was an American-British singer-songwriter and record producer who resided in England. Walker was known for his emotive voice and his unorthodox stylistic path which took him from being a teen pop icon in the 1960s to an avant-garde musician from the 1990s to his death.[2][3] Walker's success was largely in the United Kingdom, where he achieved fame as a member of pop trio the Walker Brothers, who scored several hit singles, including two number ones, during the mid-1960s, while his first four solo albums reached the top ten during the later part of the decade, with the second, Scott 2, reaching number one in 1968. He lived in the UK from 1965 onward and became a UK citizen in 1970.[4] After the Walker Brothers split in 1967, he began a solo career with the album Scott later that year, moving toward an increasingly challenging style on late 1960s baroque pop albums such as Scott 3 and Scott 4 (both 1969).[5][6] After sales of his solo work started to decrease, he reunited with the Walker Brothers in the mid-1970s.[2][3] The reformed band achieved a top ten single with 'No Regrets' in 1975, while their last album Nite Flights (1978) marked the beginning of Walker taking his music in a more avant-garde direction. After a few years hiatus, Walker revived his solo career in the mid-1980s, progressing his work further towards the avant-garde;[6][7][8] of this period in his career, The Guardian said 'imagine Andy Williams reinventing himself as Stockhausen'.[3] Walker's 1960s recordings were highly regarded by the 1980s UK underground music scene, and gained a cult following. Walker continued to record until 2018. He was described by the BBC upon his death as 'one of the most enigmatic and influential figures in rock history'."

nlp = spacy.load("en_core_web_sm")

rows = [
    {"id": "quadeca_intro", "text": text1},
    {"id": "scott_intro", "text": text2}
]

df = pd.DataFrame(rows)

docs = list(nlp.pipe(df["text"].tolist()))
df["entities"] = [[(ent.text, ent.label_) for ent in doc.ents] for doc in docs]

keep = {"PERSON", "ORG", "PRODUCT", "WORK_OF_ART", "GPE", "LOC"}

df["filtered_entities"] = [
    [(ent.text, ent.label_) for ent in doc.ents if ent.label_ in keep]
    for doc in docs
]

def normalize_dedup(ents):
    seen = set()
    out = []
    for text, label in ents:
        key = (text.strip().lower(), label)
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out

df["normalized_entities"] = df["filtered_entities"].apply(normalize_dedup)

from collections import Counter

df["entity_counts"] = df["filtered_entities"].apply(
    lambda ents: dict(Counter(text.strip().lower() for text, _ in ents))
)

ents_0 = set(df.loc[0, "entity_counts"].keys())
ents_1 = set(df.loc[1, "entity_counts"].keys())

shared = ents_0 & ents_1
print(shared)

counts_0 = df.loc[0, "entity_counts"]
counts_1 = df.loc[1, "entity_counts"]

weighted_shared = {
    ent: min(counts_0[ent], counts_1[ent])
    for ent in counts_0.keys() & counts_1.keys()
}

print(weighted_shared)