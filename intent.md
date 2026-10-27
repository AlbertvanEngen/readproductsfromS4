# Product Master Data AI Agent for Sales Representatives

SAP S/4HANA Public Cloud Edition — Natural Language Product Lookup

## Business challenge

Sales Representatives spend too much time finding product master data because information is spread across different systems. An AI agent embedded in SAP S/4HANA will allow Sales Reps to ask natural language questions and receive instant, accurate answers about product details directly within their existing workflow.

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Time to find product information | 5 minutes | Under 30 seconds | — | Product master data lookup during sales cycle | user |

## Key Milestones

1. **API Connection** — Agent successfully connected to SAP S/4HANA Product Master Data API and returning product records.
2. **Natural Language Understanding** — Agent correctly interprets and answers natural language product queries (e.g. "What is the unit of measure for product X?").
3. **Joule Embedding** — Agent accessible to Sales Reps inside SAP S/4HANA via Joule/Copilot interface.
4. **User Acceptance** — Sales Representatives validate the agent in a test environment and confirm it meets their needs.
5. **Production Go-Live** — Agent deployed and actively used by the sales team in production.

## Business Architecture (RBA)

### End-to-End Process

Lead to Cash Standard B2B

### Process Hierarchy

```
Lead to Cash Standard B2B (E2E)
└── Plan to Optimize Marketing and Sales (Phase)
    └── Plan prices and promotions (BPS-359_002)
        └── Plan and define sales prices
```

### Summary

Sales Representatives using natural language queries to retrieve product master data maps to the Lead to Cash Standard B2B E2E — specifically the Plan prices and promotions sub-process, where accurate product information is essential for Sales Reps to engage effectively in the sales cycle.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Webhook API ORD ID | Data Product ORD ID | Gap? | Notes / assumptions |
| ---------------------- | ----------------------- | ---------- | ----------------- | ------------------ | ------------------ | ------------------- | ---- | ------------------- |
| Retrieve basic product details (description, category, unit of measure) | SAP S/4HANA Cloud Public Edition — Sales Price Planning and Definition (SC1044) | `sap.s4:apiResource:API_PRODUCT_SRV:v1` | — | — | — | — | No | OData API available; custom agent integration required |
| Retrieve product classification & technical specifications | SAP S/4HANA Cloud Public Edition | `sap.s4:apiResource:API_CLFN_PRODUCT_SRV:v1` | — | — | — | — | No | OData API available; custom agent integration required |
| Natural language query interface for Sales Reps | No standard SAP product | — | — | — | — | — | Yes | Custom AI agent (Python, A2A) must be built |
| Embedded experience in SAP S/4HANA (Joule) | SAP Joule / Copilot runtime | — | — | — | — | — | Maybe | Agent must follow A2A protocol for Joule embedding |

### Key findings

- SAP S/4HANA Cloud Public Edition provides the authoritative source for product master data via the `API_PRODUCT_SRV` OData API.
- No pre-built MCP servers exist for the identified product master data APIs — custom tool integrations are required in the agent.
- Pricing and availability APIs are available (`SALESPRICE_0001`, `CE_API_PRODUCT_AVAILY_INFO_0001`) but out of scope per user confirmation (basic product details only).
- The natural language interface is a capability gap that requires a custom AI agent built with Python (A2A protocol).
- The agent must be instrumented for embedding in SAP Joule/Copilot to fulfil the embedded-experience requirement.
- A2A protocol compliance is mandatory for the agent to be surfaced inside SAP S/4HANA.

## Recommendations

### AI Agent for Product Master Data Queries

#### Executive Summary

Pro-code Python agent using S/4HANA Product Master API for NL queries

#### Recommended Solution

Build a Python-based AI agent (A2A protocol) that connects to the SAP S/4HANA Cloud Public Edition Product Master Data OData API (`API_PRODUCT_SRV`). The agent accepts natural language questions from Sales Representatives, translates them into API calls, and returns concise, readable answers. It is embedded in SAP S/4HANA via the Joule/Copilot runtime using the A2A protocol.

#### Problem Statement

Product master data is spread across multiple systems and screens in SAP S/4HANA, making it slow for Sales Representatives to find relevant product information during customer interactions. The current process takes approximately 5 minutes per lookup.

#### Affected User Roles

- Sales Representatives (primary users)
- Sales Managers (secondary — benefit from faster team response times)

#### Important factors

##### Reduces manual effort through conversational access

Sales Reps can ask questions in plain language (e.g. "What is the weight of product XYZ?") without navigating complex SAP screens or knowing technical field names.

##### Integrates directly into the existing SAP S/4HANA workflow

The agent is embedded in Joule, meaning Sales Reps do not need to switch to a separate tool — the experience is within their existing system.

##### Single source of truth from SAP S/4HANA

All product data is retrieved in real time from the authoritative SAP S/4HANA system, eliminating reliance on outdated spreadsheets or separate knowledge bases.

#### Potential risks

##### API scope limited to standard product master fields

The `API_PRODUCT_SRV` OData service covers standard product master fields. Custom or extended fields may not be available through this API without additional configuration.

##### Joule embedding requires A2A protocol compliance

The agent must strictly follow the A2A protocol to be surfaced inside SAP Joule. Any deviation may prevent successful embedding.

#### Recommended solution category

AI Agent

#### Intent fit

92%
