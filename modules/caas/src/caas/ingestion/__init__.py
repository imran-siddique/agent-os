"""
Ingestion module initialization.
"""

from caas.ingestion.processors import (
    BaseProcessor,
    PDFProcessor,
    HTMLProcessor,
    CodeProcessor,
    ProcessorFactory,
)
from caas.ingestion.structure_parser import StructureParser

__all__ = [
    "BaseProcessor",
    "PDFProcessor",
    "HTMLProcessor",
    "CodeProcessor",
    "ProcessorFactory",
    "StructureParser",
]
