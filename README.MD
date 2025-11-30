# Rootify 2.0 — Data-Driven Artist Influence Analysis (Work in Progress)

Rootify 2.0 is an end-to-end data science project that analyzes an artist’s **musical influences, themes, and stylistic patterns** using information extracted from open data sources.  
This repository currently contains **prep work, experiments, and prototypes** for the core pipeline.

## Project Overview
Rootify 2.0 aims to:
- Collect artist-related text data from **Wikipedia**, **MusicBrainz**, and **YouTube transcripts**
- Clean and normalize raw text into structured datasets  
- Apply **NLP techniques**, including embeddings and topic modeling, to extract themes
- Identify potential influences using entity detection + text pattern analysis  
- Generate useful **visualizations** such as influence graphs and theme clusters  

The final goal is to build a reproducible pipeline that takes an artist name as input and returns **interpretable, data-driven insights**.

## Current Status
This repository is in its **pre-project phase**.  

## Tech Stack (Planned)
- **Python**
- **pandas**, **numpy**
- **spaCy**, **NLTK**, **sentence-transformers**
- **BERTopic** / **scikit-learn**
- **NetworkX**, **matplotlib**
- **FastAPI** (optional)
- **Docker** + **AWS** (optional)

## Roadmap
- [ ] Complete pre-project skill practice  
- [ ] Build text-ingestion scripts  
- [ ] Create initial cleaning + NLP pipeline  
- [ ] Implement embeddings + similarity logic  
- [ ] Extract influence entities  
- [ ] Build graph & cluster visualizations  
- [ ] Integrate the full pipeline  
- [ ] Add FastAPI wrapper (optional)  
- [ ] Dockerize + deploy (stretch goal)  

## Notes
This README is temporary and will be updated as Rootify 2.0 takes shape.  
Project structure, documentation, and long-term goals will evolve as more components are built and validated.
