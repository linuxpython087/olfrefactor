from shared.value_objects import ExtractionID


class RunExtraction:
    def __init__(self, pipeline):
        self.pipeline = pipeline

    def execute(self, document_id):
        self.pipeline.run(document_id)
