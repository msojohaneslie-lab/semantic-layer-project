from google import genai
import yaml
import json
from pathlib import Path
import os
from dotenv import load_dotenv
# --------------------------------
# SETUP
# --------------------------------


BASE_DIR = Path(__file__).parent

load_dotenv(BASE_DIR / ".env")

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


YAML_FOLDER = BASE_DIR / "yaml_list"


EMBEDDING_MODEL = "gemini-embedding-001"


load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY was not found")

client = genai.Client(
    api_key=api_key
)

# --------------------------------
# CREATE TEXT FOR EMBEDDING
# --------------------------------

def create_feature_text(data):

    text = []

    text.append(f"Name: {data.get('name', '')}")
    text.append(f"Description: {data.get('description', '')}")
    # text.append(f"Entity: {data.get('entity', '')}")
    # text.append(f"Domain: {data.get('domain', '')}")
    # text.append(f"Domain: {data.get('ttl', '')}")

    # Tags
    # tags = data.get("tags", [])

    # if tags:
    #     text.append(
    #         "Tags: " + ", ".join(str(tag) for tag in tags)
    #     )

    # # Feature fields
    # text.append("Feature fields:")

    # for field in data.get("feature_fields", []):

    #     text.append(
    #         f"Field name: {field.get('name', '')}"
    #     )

    #     text.append(
    #         f"Description: {field.get('description', '')}"
    #     )

        # text.append(
        #     f"Business logic: {field.get('business_logic', '')}"
        # )

    return "\n".join(text)


# --------------------------------
# BUILD EMBEDDINGS
# --------------------------------

def build_embeddings():

    output_path = BASE_DIR / "field_descriptions_embeddings.json"

    # Load existing embeddings if they exist
    if output_path.exists():

        with open(output_path, "r", encoding="utf-8") as file:
            embeddings = json.load(file)

    else:

        embeddings = {}

    for yaml_path in YAML_FOLDER.glob("*.yaml"):

        filename = yaml_path.name

        # --------------------------------
        # SKIP ALREADY EMBEDDED FILES
        # --------------------------------

        if filename in embeddings:

            print(f"Skipping: {filename}")
            continue

        print(f"Embedding: {filename}")

        # --------------------------------
        # READ YAML
        # --------------------------------

        with open(yaml_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        text = create_feature_text(data)

        # --------------------------------
        # CREATE EMBEDDING
        # --------------------------------

        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text
        )

        vector = result.embeddings[0].values

        embeddings[filename] = vector

        # --------------------------------
        # SAVE IMMEDIATELY
        # --------------------------------

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(embeddings, file)

        print(f"Saved: {filename}")

if __name__ == "__main__":
    build_embeddings()