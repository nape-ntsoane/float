# Float

A rule based engine, built for the Standard Bank PPB Technology Graduate Assessment (Digital Platforms stream), that computes a customer's true available balance from a month of transaction data, tracks spend against it, and raises notifications (impulse flags, month end projections, threshold alerts, affordability checks, commitment tracking) as the month plays out.

## Running it

```
uv sync
cp .env.example .env
uv run python serve.py
uv run pytest
```

The API comes up on http://localhost:8080. Everything in .env has a working default, copying it over is only needed if you want to change something.

The case study's Transaction_DP.txt needs to sit in the data folder before the engine has anything to process. See data/README.md for what it expects.

## How it's put together

Everything lives under app, with main.py wiring up the FastAPI app and registering the routers.

api holds the routers, kept thin, one per feature area. They take the request and hand it straight to a service, nothing more.

core holds app wide setup, right now just settings loaded from environment variables (see .env.example).

models holds the internal data shapes, transactions, notifications, commitments, the running state object. No logic in here, just structure.

schemas holds the request and response shapes for the API, kept separate from the internal models above since what a client sends or receives isn't always the same shape the engine works with internally.

repositories is where the transaction data gets read from disk.

services is where the actual work happens, classifying transactions, computing the true available balance, tracking spend as the month progresses, checking affordability, composing the plain language messages that go back to the customer.

rules holds the seven rule evaluators, available balance tracking, impulse detection, trajectory projection, threshold alerts, affordability checks, commitment tracking, and recognising positive behaviour. Each one reads the current state and decides whether it has something to say. None of them touch the state directly.

engine ties everything together, replaying the month's events in the order they'd actually happen, so a rule only ever sees the information that would genuinely have been available at that point in time.

constants holds the category mappings and thresholds, so nothing important is a number buried somewhere in the middle of a function.

tests covers all of the above, and data is where the source transaction file goes.
