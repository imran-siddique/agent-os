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

__all__ = [
    "BaseProcessor",
    "PDFProcessor",
    "HTMLProcessor",
    "CodeProcessor",
    "ProcessorFactory",
]
