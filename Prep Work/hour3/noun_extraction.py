import spacy 
nlp = spacy.load("en_core_web_sm")

text = "Benjamin Fernando Barajas Lasky (born October 2, 2000), better known by his stage name Quadeca (formerly QuadecaX8), is an American singer, songwriter, rapper and record producer. Lasky began on the Internet by uploading rap songs, music videos, comedy sketches, and video game gameplay to his YouTube channel. Quadeca deviated away from his YouTube career to focus on his music career, releasing four mixtapes prior to the albums Voice Memos in 2019, From Me to You in 2021, I Didn't Mean to Haunt You in 2022, and Vanisher, Horizon Scraper in 2025. The mixtape Scrapyard, released on February 16, 2024, contains features from Brakence and Kevin Abstract. His fourth studio album, Vanisher, Horizon Scraper, was released in July 2025, and contains features from Danny Brown, Maruja and Olēka."

doc = nlp(text)

filtered_chunks = []
for chunk in doc.noun_chunks:
    print(chunk.text)
    if chunk.root.pos_ != 'PRON':
        if len(chunk.text.split()) >= 2:
            filtered_chunks.append(chunk.root.lemma_)

print(filtered_chunks)