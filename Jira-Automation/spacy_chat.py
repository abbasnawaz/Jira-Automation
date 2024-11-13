import spacy
from spacy.pipeline import EntityRuler
import streamlit as st

nlp = spacy.load("en_core_web_lg")

ruler = nlp.add_pipe("entity_ruler", before="ner")

patterns = [
    {"label": "PROJECT", "pattern": "project"},
    {"label": "PROJECT", "pattern": [{"LOWER": "all"}, {"LOWER": "projects"}]},
    {"label": "PROJECT", "pattern": [{"LOWER": "project"}, {"IS_ALPHA": True}]},

    {"label": "EMPLOYEE", "pattern": "employee"},
    {"label": "EMPLOYEE", "pattern": "employees"},
    {"label": "EMPLOYEE", "pattern": "team members"},
    {"label": "EMPLOYEE", "pattern": [{"LOWER": "all"}, {"LOWER": "employees"}]},

    {"label": "WORKLOG", "pattern": "worklog"},
    {"label": "WORKLOG", "pattern": "worklogs"},
    {"label": "WORKLOG", "pattern": [{"LOWER": "all"}, {"LOWER": "worklogs"}]},

    {"label": "DATE", "pattern": "today"},
    {"label": "DATE", "pattern": "yesterday"},
    {"label": "DATE", "pattern": "last week"},
    {"label": "DATE", "pattern": "last month"},
    {"label": "DATE", "pattern": "this week"},
    {"label": "DATE", "pattern": "this month"},
    {"label": "DATE", "pattern": [{"LOWER": "from"}, {"ENT_TYPE": "DATE"}, {"LOWER": "to"}, {"ENT_TYPE": "DATE"}]},  # "from [date] to [date]"

    {"label": "ISSUE", "pattern": [{"TEXT": {"REGEX": "^[A-Z]+-[0-9]+$"}}]},
    {"label": "DATE", "pattern": [{"LOWER": "from"}, {"ENT_TYPE": "DATE"}]},
    {"label": "DATE", "pattern": [{"LOWER": "to"}, {"ENT_TYPE": "DATE"}]},
]

ruler.add_patterns(patterns)


def extract_entities(query):
    doc = nlp(query)
    entities = {}

    for ent in doc.ents:
        entities[ent.label_] = ent.text

    return entities

st.title("Worklog Query Entity Extraction")

user_query = st.text_input("Enter your query:", "Show me the worklogs for all employees for last week.")

if user_query:
    extracted_entities = extract_entities(user_query)

    if extracted_entities:
        st.write("Extracted Entities:")
        for label, entity in extracted_entities.items():
            st.write(f"{label}: {entity}")
    else:
        st.write("No entities found.")
