"""Custom data type sused by the package."""

from dataclasses import asdict, dataclass
from enum import Enum, auto
from typing import Any, Self

import pandas as pd


# Configuration
class Sections(Enum):
    """Sections with iterative numbers for ordering."""

    SQUIRRELS = auto()
    BEAVERS = auto()
    CUBS = auto()
    SCOUTS = auto()


class ScheduleType(Enum):
    """Types of payment schedules on OSM."""

    SUBSCRIPTIONS = auto()
    ACTIVITIES = auto()
    SUMMER = auto()


class DataColumns:
    """Centralized column name management."""

    COLUMNS_TO_KEEP = [
        "resources.description",
        "gross_amount",
        "gocardless_fees",
        "app_fees",
        "net_amount",
        "payments.metadata.Member",
    ]


@dataclass
class Payout:
    """Immutable data class to represent a payout."""

    subscriptions: pd.DataFrame
    activities: pd.DataFrame
    summer: pd.DataFrame
    date: pd.Timestamp
    gross_amount: float
    net_amount: float
    fees: float

    def to_dict(self: Self) -> dict[str, Any]:
        """Convert payout to a dictionary."""
        return {
            **asdict(self),
            "subscriptions": self.subscriptions.reset_index().to_dict(orient="records"),
            "activities": self.activities.reset_index().to_dict(orient="records"),
            "summer": self.summer.reset_index().to_dict(orient="records"),
        }
