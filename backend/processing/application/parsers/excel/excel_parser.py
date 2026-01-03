from processing.application.parsers.base import BaseDocumentParser
from processing.application.parsers.excel.fact_builder import BlindFactBuilder
from processing.application.parsers.excel.header_repair import ExcelSanitizer
from processing.application.parsers.excel.introspector import ExcelIntrospector
from processing.application.parsers.excel.normalizer import (
    ExcelNormalizer,
    TemporalUnpivotNormalizer,
)
from processing.application.parsers.excel.raw_loader import ExcelRawLoader
from processing.application.parsers.excel.semantic_analyzer import SemanticTableAnalyzer
from processing.application.parsers.excel.semantic_contracts import (
    SemanticColumn,
    SemanticDocument,
    SemanticTable,
)
from processing.application.parsers.excel.semantic_data_cleaner import (
    SemanticDataCleaner,
)
from processing.application.parsers.excel.structure_analyzer import (
    ExcelStructureAnalyzer,
)


class ExcelParser(BaseDocumentParser):
    def parse(self):
        introspection = ExcelIntrospector.inspect(self.content)

        raw = ExcelRawLoader.load(self.content)
        structured = ExcelStructureAnalyzer.analyze(raw)
        normalized = ExcelNormalizer.normalize(raw, structured)
        temp_normalize = TemporalUnpivotNormalizer.normalize(normalized)
        sanitized = ExcelSanitizer.sanitize(temp_normalize)

        semantic = SemanticTableAnalyzer.analyze(sanitized)

        cleaned_data = SemanticDataCleaner.clean_semantic_document(semantic)

        raw_facts = []

        builder = BlindFactBuilder()

        for table in cleaned_data.tables:
            for row_index, row in enumerate(table.rows):
                raw_fact = builder.build(
                    row=row,
                    source={
                        "document_id": self.document_id,
                        "sheet": table.name,
                        "parser": "excel",
                    },
                    row_index=row_index,
                )
                raw_facts.append(raw_fact)

        return raw_facts
