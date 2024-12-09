import pandas as pd
from typing import Self
from dataclasses import dataclass

SECTIONS = ['Squirrels', 'Beavers', 'Cubs', 'Scouts']

COLUMNS_TO_KEEP = ['resources.description',
            'gross_amount', 'gocardless_fees', 'app_fees', 'net_amount', 'payments.metadata.Member']

@dataclass
class Payout:
    subscriptions: pd.DataFrame
    activities: pd.DataFrame
    date: pd.Timestamp
    gross_amount: float
    net_amount: float
    fees: float

class ReadGoCardlessPayoutExport:
    def __init__(self: Self, dataframe: pd.DataFrame):
        self.data = dataframe
        self._save_date_and_drop_columns()
        self._calculate_fees()
        self._split_member_column()
        self._fill_section()
        self._fill_type()
        self._fill_event()
            
    def _save_date_and_drop_columns(self: Self):
        self.date = self.data['payouts.arrival_date'].max()
        self.data = self.data[COLUMNS_TO_KEEP]
    
    def _calculate_fees(self: Self) -> Self:
        self.data['fees'] = self.data['gocardless_fees'] + self.data['app_fees']
        self.data = self.data.drop(columns=['gocardless_fees', 'app_fees'])
        self.fees = self.data['fees'].sum()
        self.gross = self.data['gross_amount'].sum()
        self.net = self.data['net_amount'].sum()
        
        return self
    
    def _split_member_column(self: Self) -> Self:
        self.data['member'] = self.data['payments.metadata.Member'].str.split("(")
        self.data['member'] = [member_details[0] for member_details in self.data['member']]
        self.data = self.data.drop(columns='payments.metadata.Member')
        return self
    
    def _fill_section(self: Self):
        self.data['section'] = ''
        for section in SECTIONS:
            self.data.loc[self.data['resources.description'].str.contains(section, case=False), 'section'] = section
        return self
    
    def _fill_type(self: Self):
        self.data['schedule_type'] = ''
        print(self.data['resources.description'].unique())
        for s_type in ['Subscriptions', 'Activities', 'Summer']:
            self.data.loc[self.data['resources.description'].str.contains(s_type, case=False), 'schedule_type'] = s_type
        return self
    
    def _fill_event(self: Self):
        self.data['description_split'] = self.data['resources.description'].str.split(":")
        
        self.data['event'] = [
            description_details[1] 
            for description_details in self.data['description_split']
        ]
        
        self.data['event'] = self.data['event'].str.split("(")
        self.data['event'] = [
            event_details[1] 
            for event_details in self.data['event']
        ]
        
        self.data['event'] = self.data['event'].str.replace(")", "")
        
        self.data = self.data.drop(columns=['description_split'])
        
        return self
    
    def group_data(self: Self) -> pd.DataFrame:
        operations = {
            'gross_amount': 'sum',
            'net_amount': 'sum',
            'fees': 'sum',
        }
        
        subset_subs = self.data[self.data['schedule_type'] == 'Subscriptions']
        self.subs_grouped = subset_subs.groupby(['section', 'schedule_type']).agg(operations)
        
        subset_activities = self.data[self.data['schedule_type'] == 'Activities']
        self.activities_grouped = subset_activities.groupby(['section', 'schedule_type', 'event']).agg(operations)        
        return self
    
    def create_payout(self: Self):
        self.group_data()
        
        return Payout(
            subscriptions=self.subs_grouped,
            activities=self.activities_grouped,
            gross_amount=self.gross,
            net_amount=self.net,
            fees=self.fees,
            date=self.date
        )