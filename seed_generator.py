"""
seed_generator.py

Generates synthetic seed data for the marketing-analytics-foundation dbt project.
Outputs three CSVs to marketing_analytics_foundation/seeds/:
  - users.csv
  - subscription_events.csv
  - usage_events.csv

Assumptions:
  - TODO: document your generation choices here as you make them
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

fake = Faker()
random.seed(42)
Faker.seed(42)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

NUM_USERS = 1000
NUM_USAGE_EVENTS_TARGET = 15000

PLAN_TIERS = ["free", "starter", "pro"]  # must match accepted_values tests in staging
ACQUISITION_CHANNELS = ["organic", "paid_search", "referral", "social", "email"]
COUNTRIES = ["US", "GB", "CA", "AU", "DE"]

SIGNUP_DATE_START = date(2024, 1, 1)
SIGNUP_DATE_END = date(2026, 1, 1)
CURRENT_DATE = date(2026, 2, 1) # mock instead of date.today() for consistency

SEEDS_DIR = Path(__file__).parent / "marketing_analytics_foundation" / "seeds"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def random_date(start: date, end: date) -> date:
    """Return a random date between start and end (inclusive)."""
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

def churn_probability(plan_tier: str) -> float:
    """Return the probability a user on the given plan_tier will churn."""
    if plan_tier == "free":
        return 0.00  # free users cannot churn (only subscriptions for this project)
    elif plan_tier == "starter":
        return 0.23
    elif plan_tier == "pro":
        return 0.12 
    else: 
        return 0.18  # default churn probability for unknown tiers (shouldn't happen)
    
def churn_date (signup_date: date) -> date:
    """Return a churn date at least 7 days after signup_date, but prior to the end of the data range."""
    churn_start = signup_date + timedelta(days=7)
    churn_end = CURRENT_DATE - timedelta(days=1)  # churn must be in the past
    
    return random_date(churn_start, churn_end)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def generate_users(n: int) -> list[dict]:
    """
    Generate n user records.

    Each user has:
      - user_id: sequential integer starting at 1
      - signup_date: random date within SIGNUP_DATE_START..SIGNUP_DATE_END
      - acquisition_channel: random from ACQUISITION_CHANNELS
      - plan_tier: random from PLAN_TIERS
      - country: random from COUNTRIES
      - is_churned: boolean -- roughly 30% of users should be churned
      - churn_date: date after signup_date if churned, else empty string
    """
    users = []

    for i in range(1, n + 1):
        signup_date = random_date(SIGNUP_DATE_START, SIGNUP_DATE_END)
        plan_tier = random.choice(PLAN_TIERS)
        is_churned = random.random() < churn_probability(plan_tier)

        users.append({
            "user_id": i,
            "signup_date": signup_date,
            "acquisition_channel": random.choice(ACQUISITION_CHANNELS),
            "plan_tier": plan_tier,
            "country": random.choice(COUNTRIES),
            "is_churned": is_churned,
            "churn_date": churn_date(signup_date) if is_churned else ""
        })

    return users


# ---------------------------------------------------------------------------
# Subscription events
# ---------------------------------------------------------------------------

def generate_subscription_events(users: list[dict]) -> list[dict]:
    """
    Generate subscription events for each user.
    Includes:
        - trial_started on signup_date for all users
        - trial_converted for users who converted from free to paid
        - subscription_renewed monthly for users who converted, until churn or CURRENT_DATE
        - subscription_cancelled for churned users on their churn_date
        - refund_issued for a random subset of churned users shortly after their churn_date

    Returns a flat list of event dicts, each with:
      event_id, user_id, event_type, event_date, plan_tier, amount_usd
    """
    events = []
    event_id = 1

    for user in users:
        # Every user starts with the free tier
        events.append({
            "event_id": event_id,
            "user_id": user["user_id"],
            "event_type": "trial_started",
            "event_date": user["signup_date"],
            "plan_tier": "free",
            "amount_usd": 0.00,
        })
        event_id += 1

        # users convert from the trial, then renew monthly
        if user["plan_tier"] != "free":
            conversion_date = user["signup_date"] + timedelta(days=random.randint(5, 20))
            events.append({
                "event_id": event_id,
                "user_id": user["user_id"],
                "event_type": "trial_converted",
                "event_date": conversion_date,
                "plan_tier": user["plan_tier"],
                "amount_usd": 9.99 if user["plan_tier"] == "starter" else 29.99,
            })
            event_id += 1

            # renew monthly until churn or CURRENT_DATE
            end_date = user["churn_date"] if user["is_churned"] else CURRENT_DATE
            renewal_date = conversion_date + timedelta(days=30)

            while renewal_date < end_date:
                events.append({
                    "event_id": event_id,
                    "user_id": user["user_id"],
                    "event_type": "subscription_renewed",
                    "event_date": renewal_date,
                    "plan_tier": user["plan_tier"],
                    "amount_usd": 9.99 if user["plan_tier"] == "starter" else 29.99,
                })
                event_id += 1
                renewal_date += timedelta(days=30)


        # users cancel their subscription (churn)
        if user["is_churned"]:
            events.append({
                "event_id": event_id,
                "user_id": user["user_id"],
                "event_type": "subscription_cancelled",
                "event_date": user["churn_date"],
                "plan_tier": user["plan_tier"],
                "amount_usd": 0.00,
            })
            event_id += 1

            # users get refunds
            refund = random.random() < 0.07  # 7% of cancellations result in refunds
            refund_date = user["churn_date"] + timedelta(days = random.randint(1,7))
            if refund and user["plan_tier"] != "free":
                events.append({
                    "event_id": event_id,
                    "user_id": user["user_id"],
                    "event_type": "refund_issued",
                    "event_date": refund_date,
                    "plan_tier": user["plan_tier"],
                    "amount_usd": -9.99 if user["plan_tier"] == "starter" else -29.99,
                })
                event_id += 1

    return events


# ---------------------------------------------------------------------------
# Usage events
# ---------------------------------------------------------------------------

def generate_usage_events(users: list[dict]) -> list[dict]:
    # TODO: implement in a later step
    return []


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def write_csv(records: list[dict], filename: str) -> None:
    if not records:
        print(f"  [skip] {filename} -- no records to write")
        return

    SEEDS_DIR.mkdir(parents=True, exist_ok=True)
    path = SEEDS_DIR / filename

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

    print(f"  [ok] {filename}: {len(records):,} rows → {path}")


def summarise(users, sub_events, usage_events) -> None:
    """Print a quick sanity-check summary."""
    print("\n--- Summary ---")
    print(f"Users:               {len(users):>7,}")
    print(f"Subscription events: {len(sub_events):>7,}")
    print(f"Usage events:        {len(usage_events):>7,}")

    churned = sum(1 for u in users if u["is_churned"])
    print(f"Churned users:       {churned:>7,}  ({churned/len(users)*100:.1f}%)")

    user_ids = {u["user_id"] for u in users}
    sub_orphans = [e for e in sub_events if e["user_id"] not in user_ids]
    usage_orphans = [e for e in usage_events if e["user_id"] not in user_ids]
    print(f"Orphan sub events:   {len(sub_orphans):>7,}  (should be 0)")
    print(f"Orphan usage events: {len(usage_orphans):>7,}  (should be 0)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Generating users...")
    users = generate_users(NUM_USERS)

    print("Generating subscription events...")
    sub_events = generate_subscription_events(users)

    print("Generating usage events...")
    usage_events = generate_usage_events(users)

    summarise(users, sub_events, usage_events)

    print("\nWriting CSVs...")
    write_csv(users, "users.csv")
    write_csv(sub_events, "subscription_events.csv")
    write_csv(usage_events, "usage_events.csv")

    print("\nDone.")
