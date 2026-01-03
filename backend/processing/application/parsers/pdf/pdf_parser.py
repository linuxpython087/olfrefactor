import io
import os

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import (
    DocumentConverter,
    DocumentStream,
    PdfFormatOption,
)
from processing.application.parsers.base import BaseDocumentParser
from processing.application.parsers.excel.fact_builder import BlindFactBuilder, RawFact


class PdfParser(BaseDocumentParser):
    def _create_converter(self):
        """Cree et configure le convertisseur Docling"""
        options = PdfPipelineOptions()
        options.do_ocr = True
        options.do_table_structure = True

        return DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
        )

    def parse(self) -> list[RawFact]:
        # Configuration Docling
        converter = self._create_converter()

        print(f"--- Processing: {self.filename} ---")

        pdf_stream = io.BytesIO(self.content)
        source = DocumentStream(name=self.filename, stream=pdf_stream)

        result = converter.convert(source)
        RawFactList = []
        builder = BlindFactBuilder()

        # compteur pour numéro de ligne dans une page
        current_page = 1
        line_index = 1
        # parcours des textes extraits
        for i, element in enumerate(result.document.texts):
            text_content = element.text.strip()
            page_number = 1
            # gestion de la pagination
            if element.prov and len(element.prov) > 0:
                page_number = element.prov[0].page_no
            # reset du compteur de ligne si nouvelle page
            if page_number != current_page:
                current_page = page_number
                line_index = 1

            if len(text_content) > 10:  # seuil pour eviter valeur noon significative
                fact = builder.build(
                    row={"text": text_content},
                    source={"file": self.filename, "sheet": page_number},
                    row_index=line_index,
                )
                RawFactList.append(fact)
                line_index += 1

        return RawFactList
