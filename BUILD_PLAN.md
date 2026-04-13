# BUILD_PLAN.md
## marketing-analytics-foundation -- build plan and progress tracker

This document is the working plan for building out this project. It exists so the build is intentional rather than improvised, and so anyone reading the repo can understand where it's headed even while it's in progress.

---

## Guiding principles

- Every modeling decision should be explainable in plain English
- The staging layer cleans and renames -- nothing more
- Business logic lives in intermediate models, not marts
- Marts answer a specific business question -- name them accordingly
- Tests are not optional
- The README and this document stay current as the project evolves

---

## Phase 0 -- project scaffolding
*Goal: a working dbt project connected to Snowflake with nothing in it yet*

- [ ] Create Snowflake trial account and configure warehouse, database, schemas
- [ ] Initialize dbt project with `dbt init`
- [ ] Configure `profiles.yml` for Snowflake connection
- [ ] Add `dbt-utils` to `packages.yml` and run `dbt deps`
- [ ] Confirm `dbt debug` passes cleanly
- [ ] Create repo structure: `models/staging`, `models/intermediate`, `models/marts`, `seeds/`, `tests/`
- [ ] Add `.gitignore` for dbt artifacts and credentials

**Exit criteria:** `dbt debug` passes, repo is clean, folder structure is in place

---

## Phase 1 -- synthetic data generation
*Goal: realistic seed data that mirrors what a real SaaS product would produce*

### Entities to generate

**Users** (`users.csv`)
- user_id, signup_date, acquisition_channel, plan_tier, country, is_churned, churn_date

**Subscription events** (`subscription_events.csv`)
- event_id, user_id, event_type, event_date, plan_tier, amount_usd
- event_type values: trial_started, trial_converted, subscription_renewed, subscription_cancelled, refund_issued

**Usage events** (`usage_events.csv`)
- event_id, user_id, event_date, feature_used, session_duration_seconds

### Generator script (`seed_generator.py`)
- [ ] Write Python script using `faker` and `random` to generate all three entities
- [ ] Ensure referential integrity -- usage and subscription events only reference valid user_ids
- [ ] Generate ~1,000 users, ~3,000 subscription events, ~15,000 usage events
- [ ] Output as CSVs to `seeds/`
- [ ] Document generation logic and assumptions in script comments

**Exit criteria:** Three clean seed CSVs, generator script committed and documented

---

## Phase 2 -- staging layer
*Goal: clean, renamed, lightly typed versions of every source -- one model per source*

- [ ] Define sources in `models/staging/sources.yml`
- [ ] Build `stg_users.sql` -- cast types, rename to snake_case, no logic
- [ ] Build `stg_subscription_events.sql` -- cast types, rename, parse event_type
- [ ] Build `stg_usage_events.sql` -- cast types, rename, parse feature_used
- [ ] Add source freshness tests to `sources.yml`
- [ ] Add basic `not_null` and `unique` tests for primary keys on all staging models
- [ ] Add `accepted_values` tests for event_type and plan_tier columns
- [ ] Run `dbt test` -- all tests pass

**Naming convention:** `stg_[source]__[entity].sql`

**Exit criteria:** All staging models build, all tests pass, sources documented in yml

---

## Phase 3 -- intermediate layer
*Goal: encode business logic and build the joined, derived datasets that marts will consume*

- [ ] Build `int_user_subscriptions.sql`
  - Join users to subscription events
  - Derive subscription status, trial conversion flag, days to conversion
  - One row per user

- [ ] Build `int_user_activity.sql`
  - Join users to usage events
  - Derive session counts, last active date, days since last active
  - One row per user

- [ ] Add tests for intermediate models -- row count reasonableness, no null user_ids on joins
- [ ] Document all intermediate models in yml with column descriptions

**Exit criteria:** Both intermediate models build cleanly, join logic is documented, tests pass

---

## Phase 4 -- mart layer
*Goal: consumer-ready models that answer specific business questions*

### `mart_user_retention.sql`
- Monthly cohort retention -- users by signup month, % still active at 1/2/3/6 months
- Grain: one row per cohort month + period
- Business question: are we keeping the users we acquire, and when do we lose them?

### `mart_revenue.sql`
- MRR by month, new MRR, churned MRR, net MRR change
- Churn rate by month
- Grain: one row per month
- Business question: what does our revenue trajectory look like and where is churn coming from?

### `mart_product_engagement.sql`
- Active users by month (DAU/MAU proxy)
- Feature usage breakdown
- Power user identification (top decile by session count)
- Grain: one row per user per month
- Business question: which users are actually using the product and how?

- [ ] Build all three mart models
- [ ] Add mart-level tests -- no duplicate grain keys, revenue figures non-negative
- [ ] Document all mart models with full column descriptions and grain definitions
- [ ] Run full `dbt build` -- everything passes

**Exit criteria:** All three marts build, tests pass, every column has a description

---

## Phase 5 -- CI/CD and documentation
*Goal: automated testing on every PR and a generated dbt docs site*

### GitHub Actions workflow
- [ ] Create `.github/workflows/dbt_ci.yml`
- [ ] On pull request: run `dbt deps`, `dbt compile`, `dbt build --target ci`
- [ ] Configure a CI target in `profiles.yml` that uses a separate Snowflake schema
- [ ] Confirm workflow runs cleanly on a test PR

### dbt docs
- [ ] Run `dbt docs generate`
- [ ] Review generated docs -- all models and columns described
- [ ] Add overview docs to `docs/` folder explaining the project and data model

**Exit criteria:** CI passes on a real PR, dbt docs generate without errors, no undocumented models

---

## Phase 6 -- BI layer
*Goal: a visible output layer that shows the data is actually useful*

- [ ] Connect Metabase (or Looker Studio) to Snowflake mart layer
- [ ] Build three simple dashboards -- one per mart question
- [ ] Screenshot or embed in README so the output is visible without running the stack

**Exit criteria:** All three mart questions represented in dashboards, screenshots embedded in README, stack is fully visible end-to-end from raw seed data to BI output

---

## Decisions log

*Record significant modeling or architecture decisions here as the project progresses. Explain what was considered and why this path was chosen.*

| Date | Decision | Reasoning |
|---|---|---|
| -- | -- | -- |

---

## What's deliberately out of scope

- Real customer data of any kind
- Airflow or other orchestration -- this is a modeling and architecture project, not a pipeline operations project
- dbt Cloud -- dbt Core keeps this self-contained and reproducible
- Advanced ML or predictive modeling -- the goal is clean foundational analytics, not data science

---

*Last updated: project start*
