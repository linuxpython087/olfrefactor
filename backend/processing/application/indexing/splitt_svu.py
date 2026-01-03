from langchain_core.documents import Document


def indicator_to_text(indicator: dict) -> str:
    """
    Texte riche qui sera embedé
    """
    parts = [
        f"Indicateur : {indicator['label']}",
        f"Catégorie : {indicator['category']}",
    ]

    if indicator.get("description"):
        parts.append(f"Description : {indicator['description']}")

    if indicator.get("aliases"):
        parts.append(f"Alias : {', '.join(indicator['aliases'])}")

    if indicator.get("keywords"):
        parts.append(f"Mots-clés : {', '.join(indicator['keywords'])}")

    if indicator.get("value_type"):
        parts.append(f"Type de valeur : {indicator['value_type']}")

    if indicator.get("unit"):
        parts.append(f"Unité : {indicator['unit']}")

    return "\n".join(parts)


def split_svu_to_documents(svu: dict) -> list[Document]:
    documents = []

    for indicator in svu["indicators"]:
        text = indicator_to_text(indicator)

        metadata = {
            "indicator_id": indicator["indicator_id"],
            "indicator_code": indicator["indicator_code"],
            "category": indicator["category"],
            "value_type": indicator.get("value_type"),
            "unit": indicator.get("unit"),
        }

        documents.append(Document(page_content=text, metadata=metadata))

    return documents
