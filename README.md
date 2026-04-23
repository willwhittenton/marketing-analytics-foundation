# marketing-analytics-foundation

A reference analytics stack built to demonstrate how I think about data modeling, warehouse architecture, and analytics engineering in practice.

This is not a tutorial follow-along. It's a from-scratch implementation of a production-grade analytics foundation using a synthetic SaaS dataset -- the kind of thing I'd build on day one at an early-stage company that needed its data house put in order.

---

## What this is

A modern analytics stack built on **dbt + Snowflake**, structured around a **medallion architecture** (staging, intermediate, marts), with **GitHub Actions CI** running on every pull request.

The synthetic business context is a small B2C SaaS product -- users, subscriptions, and product usage events. Simple enough to understand quickly, realistic enough to demonstrate meaningful modeling decisions.

---

## What it demonstrates

- Medallion architecture implemented cleanly in dbt -- staging layers that clean and rename, intermediate layers that encode business logic, mart layers that answer real business questions
- Dimensional modeling instincts applied to a SaaS data model
- dbt best practices: sources, tests, documentation, packages, and a consistent naming convention throughout
- CI/CD via GitHub Actions -- dbt compile and test runs on every PR, the same way I'd set it up for a real team
- A synthetic data generator in Python so the whole stack is reproducible without needing real customer data
- End-to-end visibility from raw seed data through to Metabase dashboards -- because data that doesn't get used isn't worth building

---

## The marts answer three questions

| Mart | Business question |
|---|---|
| `mart_user_retention` | Are we keeping the users we acquire, and when do we lose them? |
| `mart_revenue` | What does our MRR look like, and where is churn coming from? |
| `mart_product_engagement` | Which users are actually using the product, and how? |

---

## Stack

- **Warehouse:** Snowflake
- **Transformation:** dbt Core
- **Orchestration:** GitHub Actions (CI), manual runs locally
- **Data generation:** Python + Faker
- **BI layer:** Metabase

---

## Project status

This project is actively being built. The structure and modeling approach are intentional and documented -- see [BUILD_PLAN.md](./BUILD_PLAN.md) for the full plan and progress tracking.

---

## Running it yourself

### Phase 0 — project scaffolding

**Prerequisites**
- Snowflake account (trial is fine) with a warehouse, database, and user configured
- dbt Core installed (`pip install dbt-snowflake`)

**1. Clone the repo and install dbt packages**

```bash
git clone https://github.com/willwhittenton/marketing-analytics-foundation.git
cd marketing-analytics-foundation/marketing_analytics_foundation
dbt deps
```

**2. Create `~/.dbt/profiles.yml`**

`profiles.yml` lives outside the project directory so credentials are never committed. Create it manually:

```yaml
marketing_analytics_foundation:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: <orgname>-<accountname>   # found under Admin → Accounts in Snowflake
      user: <your_username>
      authenticator: externalbrowser     # or swap for `password:` if not using SSO
      database: <your_database>
      warehouse: <your_warehouse>
      schema: dbt_dev
      role: <your_role>
      threads: 4
      client_session_keep_alive: false
```

**3. Verify the connection**

```bash
dbt debug
```

All checks should pass. If `Connection test` fails, double-check your `account` identifier — it must be in `orgname-accountname` format, not the legacy `accountname.region` format.

**4. Confirm `.gitignore` is in place**

`target/`, `dbt_packages/`, `logs/`, and `profiles.yml` are all covered. No credentials or compiled artifacts will be committed.

---

## Why I built this

My day job runs on Microsoft Fabric. Most early-stage companies I'm interested in working with run on Snowflake and dbt. This project closes that gap -- not just as a credential, but as an honest exercise in building something clean outside my primary stack.

The modeling decisions here reflect how I actually think: start with the business question, work backward to the grain, keep the staging layer dumb and the mart layer opinionated.

---

*Questions or feedback -- willwhittenton@gmail.com*
