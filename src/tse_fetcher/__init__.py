"""TSE data client."""

from importlib.metadata import PackageNotFoundError, version

from .client import SyncPlanItem, TseClient
from .constants import BASE_URL, DATASETS, DatasetSpec

try:
    __version__ = version("tse-fetcher")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "__version__",
    "SyncPlanItem",
    "TseClient",
    "DATASETS",
    "DatasetSpec",
    "BASE_URL",
]
