# Standard Bank PPB Technology Graduate Assessment

A rule based engine that computes a customer's true available balance from a month of transaction data, tracks spend against it, and raises notifications (impulse flags, month end projections, threshold alerts, affordability checks, commitment tracking) as the month plays out.

## Running it

```
uv sync
uv run python serve.py
uv run pytest
```

The API comes up on http://localhost:8080.

The case study's Transaction_DP.txt needs to sit in the data folder before the engine has anything to process. See data/README.md for what it expects.

## How it's put together

Everything lives under app, with main.py wiring up the FastAPI app and registering the routers.

api holds the routers, kept thin, one per feature area. They take the request and hand it straight to a service, nothing more.

models holds the data shapes, transactions, notifications, commitments, the running state object. No logic in here, just structure.

repositories is where the transaction data gets read from disk.

services is where the actual work happens, classifying transactions, computing the true available balance, tracking spend as the month progresses, checking affordability, composing the plain language messages that go back to the customer.

rules holds the seven rule evaluators, available balance tracking, impulse detection, trajectory projection, threshold alerts, affordability checks, commitment tracking, and recognising positive behaviour. Each one reads the current state and decides whether it has something to say. None of them touch the state directly.

engine ties everything together, replaying the month's events in the order they'd actually happen, so a rule only ever sees the information that would genuinely have been available at that point in time.

constants holds the category mappings and thresholds, so nothing important is a number buried somewhere in the middle of a function.

tests covers all of the above, and data is where the source transaction file goes.
