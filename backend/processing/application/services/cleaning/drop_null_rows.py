from processing.application.services.cleaning.base import DataCleaningStrategy


class DropNullRowsCleaning(DataCleaningStrategy):
    def clean(self, parsed_data):
        cleaned = {}

        for sheet, rows in parsed_data.items():
            valid_rows = []

            for row in rows:
                if all(value is not None and value != "" for value in row.values()):
                    valid_rows.append(row)

            cleaned[sheet] = valid_rows

        return cleaned
