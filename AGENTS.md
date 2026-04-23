# Agent Instructions — marketing-analytics-foundation

A production-grade dbt + Snowflake analytics stack for a synthetic B2C SaaS business. Built to demonstrate analytics engineering skills relevant to Series A/B startups (health, SaaS, fintech).

See [BUILD_PLAN.md](./BUILD_PLAN.md) for phased build plan and progress tracking.

---

## Stack

| Layer | Tool |
|---|---|
| Warehouse | Snowflake |
| Transformation | dbt Core |
| CI | GitHub Actions |
| Data generation | Python + Faker |
| BI | Metabase |

---

## Architecture — medallion layers

```
seeds/ (CSV) → models/staging/ → models/intermediate/ → models/marts/
```

| Layer | Rule |
|---|---|
| `staging/` | Cast types, rename to snake_case. **No business logic.** One model per source. |
| `intermediate/` | Joins, derivations, business logic. Feed into marts. |
| `marts/` | Consumer-ready. Answer one specific business question. Named accordingly. |

---

## Naming conventions

- Staging models: `stg_[source]__[entity].sql` (double underscore between source and entity)
- Intermediate models: `int_[description].sql`
- Mart models: `mart_[business_question].sql`
- All columns: `snake_case`
- Primary keys: `[entity]_id`

---

## Key dbt commands

```bash
dbt debug              # Verify Snowflake connection
dbt deps               # Install packages (run after cloning or adding packages)
dbt build              # Run models + tests in DAG order
dbt test               # Run tests only
dbt docs generate      # Generate documentation site
```

For CI, the workflow targets a separate Snowflake schema (`--target ci`).

---

## Testing expectations

- Every staging and mart model needs at minimum: `not_null` + `unique` on primary keys
- Staging: add `accepted_values` tests for `event_type` and `plan_tier`
- Marts: test for no duplicate grain keys, non-negative revenue figures
- All models and columns must have descriptions in `.yml` files before a phase is considered complete

---

## The three mart outputs

| Mart | Grain | Business question |
|---|---|---|
| `mart_user_retention` | cohort month + period | Are we retaining users we acquire, and when do we lose them? |
| `mart_revenue` | month | MRR trajectory and churn source |
| `mart_product_engagement` | user + month | Which users are active and how are they using the product? |

---

## Synthetic data schema

**seeds/users.csv** — `user_id, signup_date, acquisition_channel, plan_tier, country, is_churned, churn_date`

**seeds/subscription_events.csv** — `event_id, user_id, event_type, event_date, plan_tier, amount_usd`
- `event_type` values: `trial_started`, `trial_converted`, `subscription_renewed`, `subscription_cancelled`, `refund_issued`

**seeds/usage_events.csv** — `event_id, user_id, event_date, feature_used, session_duration_seconds`

Referential integrity must be maintained — usage and subscription events only reference valid `user_id`s.

---

## What is deliberately out of scope

- Real customer data
- Airflow or dbt Cloud
- ML/predictive modeling
- Orchestration beyond GitHub Actions CI

---

## Decisions log

Significant architecture decisions are tracked in the [Decisions log section of BUILD_PLAN.md](./BUILD_PLAN.md#decisions-log). Add new entries there when making non-obvious choices.
