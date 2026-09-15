# Data

This is where the case study's Transaction_DP.txt goes. The transaction repository reads it straight from here, nothing gets uploaded or parsed from the Excel workbook at runtime.

It's a JSON file with two parts. An account object holding the account details, opening balance, currency, statement period. And a statementLines array with the 59 transactions themselves, each one carrying its amount, narrative, dates, category, type, and running balance.
