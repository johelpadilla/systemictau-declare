"""systemictau-declare: freeze the protocol, declare the generator, seal FAR.

>>> from systemictau_declare import Protocol, declare
>>> P = Protocol.frozen_v1()
>>> P.weights
(0.6, 0.4)
"""

from .protocol import Protocol, protocol_hash
from .run import declare
from .schema import DeclarationReport, Seal
from .report import write_report, render_html
from .fixtures import g0_independent_ar, coupled_logistic

__version__ = "0.1.1"

__all__ = [
    "Protocol",
    "declare",
    "DeclarationReport",
    "Seal",
    "write_report",
    "render_html",
    "protocol_hash",
    "g0_independent_ar",
    "coupled_logistic",
    "__version__",
]
