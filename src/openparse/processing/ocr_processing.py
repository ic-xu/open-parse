from typing import List

from src.openparse.processing import ProcessingStep
from src.openparse.schemas import Node


class OcrProcessing(ProcessingStep):
    def process(self, nodes: List[Node]) -> List[Node]:
        pass
