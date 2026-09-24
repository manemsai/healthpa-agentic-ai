import json
from pathlib import Path


FILE = Path("data/raw/cms/ncd_details/ncd_373_v1.json")


def main():
    payload = json.loads(FILE.read_text(encoding="utf-8"))

    print("=" * 100)
    print("TOP LEVEL KEYS")
    print("=" * 100)
    print(payload.keys())

    print("\n" + "=" * 100)
    print("META")
    print("=" * 100)
    print(json.dumps(payload.get("meta", {}), indent=2))

    data = payload.get("data", [])

    print("\n" + "=" * 100)
    print("NUMBER OF DATA RECORDS")
    print("=" * 100)
    print(len(data))

    if data:
        record = data[0]

        print("\n" + "=" * 100)
        print("AVAILABLE FIELDS")
        print("=" * 100)

        for key in record.keys():
            print(key)

        print("\n" + "=" * 100)
        print("FULL NCD RECORD")
        print("=" * 100)

        print(json.dumps(record, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()