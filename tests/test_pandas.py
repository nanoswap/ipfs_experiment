import pandas as pd
import pytest
from typing import List
from src.models.store import Store


class TestPandas:

    @pytest.fixture
    def sample_data(self):
        # Create some sample Store objects for testing
        class MockRecord:
            def __init__(self, metadata, subindex):
                self.metadata = metadata
                self.subindex = subindex
                self.content = None
            
            def read(self):
                # Simulate reading content from IPFS
                self.content = "Mock content"
        
        store1 = MockRecord(
            metadata={
                'borrower': 'Alice',
                'lender': 'Bob',
                'loan': '1000',
                'state': 'active'
            },
            subindex={
                'payment': {
                    '01-01-2022': 100,
                    '02-01-2022': 100,
                    '03-01-2022': 100
                },
                'amount_due': 300,
                'due_date': '04-01-2022'
            }
        )
        
        store2 = MockRecord(
            metadata={
                'borrower': 'Charlie',
                'lender': 'David',
                'loan': '500',
                'state': 'closed'
            },
            subindex={
                'payment': {
                    '01-01-2022': 50,
                    '02-01-2022': 50,
                },
                'amount_due': 500,
                'due_date': '03-01-2022'
            }
        )
        
        return [store1, store2]

    def test_to_dataframe(self, sample_data: List[Store]):
        df = Store.to_dataframe(sample_data)
        assert isinstance(df, pd.DataFrame)
        assert df.shape == (2, 7)
        assert df.columns.tolist() == ['borrower', 'lender', 'loan', 'payment', 'amount_due', 'due_date', 'state']
        assert df['borrower'].tolist() == ['Alice', 'Charlie']
        assert df['lender'].tolist() == ['Bob', 'David']
        assert df['loan'].tolist() == ['1000', '500']
        assert df['payment'].tolist() == [{'01-01-2022': 100, '02-01-2022': 100, '03-01-2022': 100}, {'01-01-2022': 50, '02-01-2022': 50}]
        assert df['amount_due'].tolist() == [300, 500]
        assert df['due_date'].tolist() == ['04-01-2022', '03-01-2022']
        assert df['state'].tolist() == ['active', 'closed']
