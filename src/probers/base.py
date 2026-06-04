from abc import ABC, abstractmethod
from src.models import HostEntry, ProbeResult


class AbstractProber(ABC):
    @abstractmethod
    def probe(self, entry: HostEntry) -> ProbeResult:
        ...
