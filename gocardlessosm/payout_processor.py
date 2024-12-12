"""Class to prossess the payments from GoCardless into a a human readable format appropiate for the OSM system."""

import logging
from typing import Self

import pandas as pd

from gocardlessosm.data_types import DataColumns, Payout, ScheduleType, Sections


class PayoutProcessor:
    """Processes GoCardless payout export data."""

    def __init__(self: Self, dataframe: pd.DataFrame, logger: logging.Logger = None) -> None:
        """Initialize the processor with input dataframe.

        Args:
            dataframe (pd.DataFrame): Input dataframe to process
            logger (logging.Logger, optional): Logger for tracking processing steps
        """
        self.logger = logger or logging.getLogger(__name__)
        self.original_data = dataframe.copy()
        self.data = dataframe[DataColumns.COLUMNS_TO_KEEP].copy()

        self._process_data()

    def _process_data(self: Self) -> Self:
        """Execute data processing steps."""
        try:
            self._save_date()
            self._calculate_fees()
            self._process_member_column()
            self._categorize_data()
        except Exception as e:
            self.logger.error(f"Error processing data: {e}")
            raise

    def _save_date(self: Self) -> Self:
        """Extract and store payout date."""
        self.date = self.original_data["payouts.arrival_date"].max()
        self.logger.info(f"Payout date: {self.date}")

    def _calculate_fees(self: Self) -> Self:
        """Calculate total fees and financial metrics."""
        self.data["fees"] = self.data["gocardless_fees"] + self.data["app_fees"]
        self.data = self.data.drop(columns=["gocardless_fees", "app_fees"])

        self.fees = self.data["fees"].sum()
        self.gross = self.data["gross_amount"].sum()
        self.net = self.data["net_amount"].sum()

        self.logger.info(
            f"Financial Summary: Gross ${self.gross:.2f}, Net ${self.net:.2f}, Fees ${self.fees:.2f}"
        )

    def _process_member_column(self: Self) -> Self:
        """Clean and extract member information."""
        self.data["member"] = self.data["payments.metadata.Member"].str.split("(").str[0]
        self.data = self.data.drop(columns="payments.metadata.Member")

    def _categorize_data(self: Self) -> Self:
        """Categorize data by section, type, and event."""
        self._categorize_sections()
        self._categorize_schedule_types()
        self._extract_events()

    def _categorize_sections(self: Self) -> Self:
        """Categorize data into different sections."""
        self.data["section"] = ""
        for section in Sections:
            mask = self.data["resources.description"].str.contains(section.name, case=False)
            self.data.loc[mask, "section"] = section.name

    def _categorize_schedule_types(self: Self) -> Self:
        """Categorize schedule types."""
        self.data["schedule_type"] = ""
        for schedule_type in ScheduleType:
            mask = self.data["resources.description"].str.contains(schedule_type.name, case=False)
            self.data.loc[mask, "schedule_type"] = schedule_type.name

    def _extract_events(self: Self) -> Self:
        """Extract event details from description."""

        def clean_event(description: str) -> str:
            """Helper function to clean event names."""
            try:
                # Split by ':' and take the second part
                event = description.split(":")[1].split("(")[1].split(")")[0]
                return event.strip()
            except (IndexError, AttributeError):
                return ""

        self.data["event"] = self.data["resources.description"].apply(clean_event)

    def group_data(self: Self) -> Self:
        """Group data by different categories."""
        operations = {
            "gross_amount": "sum",
            "net_amount": "sum",
            "fees": "sum",
        }

        print(self.data["schedule_type"].unique())

        # Group subscriptions
        subset_subs = self.data[self.data["schedule_type"] == ScheduleType.SUBSCRIPTIONS.name]
        self.subs_grouped = subset_subs.groupby(["section", "schedule_type"]).agg(operations)

        # Group activities
        subset_activities = self.data[self.data["schedule_type"] == ScheduleType.ACTIVITIES.name]
        self.activities_grouped = subset_activities.groupby(
            ["section", "schedule_type", "event"]
        ).agg(operations)

        # Group activities
        subset_summer = self.data[self.data["schedule_type"] == ScheduleType.SUMMER.name]
        self.summer_grouped = subset_summer.groupby(["section", "schedule_type", "event"]).agg(
            operations
        )

        return self

    def organise_data(self: Self) -> dict[str, list[dict[str, str]]]:
        """Organize grouped data so the sections are a logical order.

        Returns:
            dict[str, list[dict[str, str]]]: _description_
        """
        self.subs_grouped = self.subs_grouped.reset_index()
        self.subs_grouped["section_number"] = self.subs_grouped["section"].apply(
            lambda x: Sections[x].value
        )
        self.subs_grouped = self.subs_grouped.sort_values(by="section_number").set_index(
            "section", drop=True
        )
        self.subs_grouped = self.subs_grouped.drop(columns=["section_number", "schedule_type"])

        self.activities_grouped = self.activities_grouped.reset_index()
        self.activities_grouped["section_number"] = self.activities_grouped["section"].apply(
            lambda x: Sections[x].value
        )
        self.activities_grouped = self.activities_grouped.sort_values(by="section_number")
        self.activities_grouped = self.activities_grouped.drop(
            columns=["section_number", "schedule_type"]
        )

        return self

    def create_payout(self: Self) -> Payout:
        """Create a Payout object with processed data."""
        self.group_data()
        self.organise_data()

        return Payout(
            subscriptions=self.subs_grouped,
            activities=self.activities_grouped,
            summer=self.summer_grouped,
            gross_amount=self.gross,
            net_amount=self.net,
            fees=self.fees,
            date=self.date,
        )


def process_gocardless_export(df: pd.DataFrame) -> Payout:
    """Convenience function to process a GoCardless export file.

    Args:
        df (pd.DataFrame): Dataframe containing GoCardless export data

    Returns:
        Payout: Processed payout data
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s")
    logger = logging.getLogger(__name__)

    try:
        # Process the dataframe
        processor = PayoutProcessor(df, logger)
        payout = processor.create_payout()

        return payout

    except Exception as e:
        logger.error(f"Failed to process export: {e}")
        raise
