from pathlib import Path


SOURCE = Path("flashcards.txt")
TARGET = Path("flashcards_anki_import.txt")


def flatten_field(field: str) -> str:
    """Make one TSV field safe for Anki's line-based importer."""
    field = field.replace("\r\n", "\n").replace("\r", "\n")
    field = field.replace("\n", "<br>")
    field = field.replace("\t", "    ")
    return field.strip()


def main() -> None:
    rows: list[list[str]] = []
    header_lines: list[str] = []

    with SOURCE.open("r", encoding="utf-8-sig", newline="") as source:
        card_text_lines: list[str] = []
        reading_headers = True
        for line in source:
            if reading_headers and line.startswith("#"):
                header_lines.append(line.rstrip("\r\n"))
            else:
                reading_headers = False
                card_text_lines.append(line.rstrip("\r\n"))

    records: list[str] = []
    i = 0
    while i < len(card_text_lines):
        line = card_text_lines[i]
        i += 1

        if not line.strip():
            continue

        if not line.startswith('"'):
            raise ValueError(f"Malformed card start: {line[:120]!r}")

        record_lines = [line]
        while '"\tInfo2::' not in record_lines[-1]:
            if i >= len(card_text_lines):
                raise ValueError(f"Unterminated card: {record_lines[0][:120]!r}")
            record_lines.append(card_text_lines[i])
            i += 1

        records.append("\n".join(record_lines))

    for record in records:
        body, tag_suffix = record.rsplit('"\tInfo2::', 1)
        tag = "Info2::" + tag_suffix

        if '"\t"' not in body:
            raise ValueError(f"Could not find front/back separator: {body[:120]!r}")

        front_part, back = body.split('"\t"', 1)
        front = front_part[1:]

        rows.append([flatten_field(front), flatten_field(back), flatten_field(tag)])

    with TARGET.open("w", encoding="utf-8", newline="\n") as target:
        for line in header_lines:
            target.write(line + "\n")

        for row in rows:
            target.write("\t".join(row) + "\n")

    print(f"Wrote {len(rows)} cards to {TARGET}")


if __name__ == "__main__":
    main()
