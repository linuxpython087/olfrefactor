import json


def load_svu(path: str = "./processing/application/indexing/svu.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    print(load_svu())
