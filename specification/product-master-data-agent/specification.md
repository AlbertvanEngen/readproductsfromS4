# Specification: product-master-data-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [x] Read the project input (`product-requirements-document.md`, `intent.md`)
- [x] Bootstrap agent code in `assets/product-master-data-agent/` using instructions from the sap-agent-bootstrap section. (invoke from inside `assets/product-master-data-agent/`, use copy commands — do NOT create files manually)
- [x] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

> **Before proceeding**, read [guidelines-agent-skills.md](../guidelines-agent-skills.md) and decide — based on the PRD — whether the agent needs runtime skills.

- [x] Evaluate whether a runtime skill is needed for product lookup workflows or domain-specific SAP field knowledge
- [x] If needed, create `assets/product-master-data-agent/app/skills/product-lookup/SKILL.md` with step-by-step instructions for interpreting product queries, including how to handle ambiguous product identifiers (name vs. number)

---

## Project-Specific Tasks

### System Prompt

- [x] Open `assets/product-master-data-agent/app/agent.py` and write the system prompt `@prompt_section` body (`get_system_prompt`) to define the agent's role and behaviour:
  - The agent is a product master data assistant for Sales Representatives, embedded in SAP S/4HANA via Joule
  - It answers natural language questions about SAP product master data using the available MCP tools
  - It covers: product name/description, product category/group, base unit of measure, product type, and other standard product master fields
  - It must NEVER fabricate product data — if a product is not found or data is unavailable, it must say so explicitly
  - It must decline questions about pricing, stock availability, or any topic outside product master data, and suggest where the user can find that information
  - It must never create, update, or delete product records
  - Responses must be concise and formatted for a sales context (clear, human-readable, no raw JSON)

### Natural Language Product Query (R1)

- [x] Implement a `search_products` tool in `assets/product-master-data-agent/app/` that:
  - Accepts a natural language description or product name fragment
  - Calls the MCP tool wrapping `API_PRODUCT_SRV` to search/list products by description or material number
  - Returns a list of matching products with key fields: product number, description, product group, base unit of measure, product type
- [x] Implement a `get_product_details` tool in `assets/product-master-data-agent/app/` that:
  - Accepts a product number (material number)
  - Calls the MCP tool wrapping `API_PRODUCT_SRV` to retrieve full product master details for that number
  - Returns all standard product master fields relevant to a Sales Representative

### Real-Time Data Retrieval from SAP S/4HANA (R2)

- [x] All product data retrieval MUST go through the generated MCP server wrapping `API_PRODUCT_SRV` — no direct HTTP clients or OData calls
- [x] Ensure the agent's tools invoke MCP tools at runtime using `get_mcp_tools()` from the `mcp_tools` module
- [x] Handle API errors gracefully: if the MCP tool returns an error or empty result, the agent must relay the issue to the user in plain language rather than silently failing

### Graceful Handling of Unanswerable Questions (R4)

- [x] Add guardrail logic in the system prompt to instruct the agent to:
  - Explicitly state when a question is outside its scope (pricing, availability, product creation)
  - Suggest the correct SAP transaction or team for out-of-scope queries
  - State clearly when a product is not found in SAP S/4HANA
- [x] Verify the agent does not attempt to answer pricing or availability queries by testing with relevant prompts

### Coverage of Standard Product Master Fields (R5)

- [x] Confirm the `get_product_details` tool returns at minimum:
  - `Product` (material number)
  - `ProductDescription` (base language description)
  - `ProductGroup`
  - `BaseUnit` (base unit of measure)
  - `ProductType`
  - `Division`
  - `GrossWeight` and `NetWeight` (if available in the API response)
- [x] Validate the agent correctly maps user-friendly field names (e.g. "unit of measure", "category") to the correct SAP API fields

---

## API Integration

### MCP API Integration

```
MCP API: sap.s4:apiResource:API_PRODUCT_SRV:v1
MCP tool scope: read-only
Resources in scope: A_Product, A_ProductDescription, A_ProductPlant, A_ProductBasicText
```

- API spec downloaded to: `specification/product-master-data-agent/api-specs/API_PRODUCT_SRV.edmx`

---

## Business Instrumentation

- [x] Implement business step instrumentation for each milestone from the PRD using structured logging (`[MILESTONE_ID].[achieved|missed]: [description]`) and OpenTelemetry custom spans. See [guidelines-agent-python.md](../guidelines-agent-python.md) for Python-specific implementation details.

  Milestones to instrument:
  - **M1 — API Connection**: emit `M1.achieved: SAP S/4HANA Product Master API connection verified — product records retrieved successfully` on first successful API call; emit `M1.missed: SAP S/4HANA Product Master API connection failed — check credentials, system URL, or API availability` on failure
  - **M2 — Natural Language Understanding**: emit `M2.achieved: Natural language query resolved — product data returned successfully for user question` when the agent returns a valid product answer; emit `M2.missed: Natural language query not resolved — intent unclear or API returned no matching record` when the query cannot be fulfilled
  - **M3 — Joule Embedding**: emit `M3.achieved: Agent embedded in Joule — Sales Rep interaction via Joule interface successful` when a Joule-proxied request succeeds; emit `M3.missed: Joule embedding not verified — A2A protocol compliance or registration issue detected` on A2A validation failure
  - **M4 — User Acceptance**: emit `M4.achieved: User acceptance testing passed — Sales Rep sign-off received` upon UAT completion; emit `M4.missed: User acceptance testing not completed or issues raised by Sales Representatives` if UAT fails
  - **M5 — Production Go-Live**: emit `M5.achieved: Agent live in production — product master data queries being served to Sales Representatives` upon production deployment; emit `M5.missed: Production go-live delayed or blocked — review deployment status and outstanding issues` on deployment failure

- [x] Verify `bootstrap(app)` is called after `app = server.build()` in `main.py`

---

## MCP Tool Integration

> Read [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) for complete MCP integration patterns.

- [x] Verify `specification/product-master-data-agent/api-specs/API_PRODUCT_SRV.edmx` exists (already downloaded)
- [x] Invoke `mcp-translation-file` skill to generate a translation card from `specification/product-master-data-agent/api-specs/API_PRODUCT_SRV.edmx`
- [x] Invoke `setup-solution` skill to create `solution.yaml` and register the generated MCP server asset
- [x] Wire MCP tool loading in `agent.py` using `get_mcp_tools()` from the `mcp_tools` module — see [guidelines-agent-python.md](../guidelines-agent-python.md) for canonical pattern. NEVER import directly from `sap_cloud_sdk.agentgateway`. NEVER create direct HTTP clients.
- [x] Add the generated MCP server as a dependency in `asset.yaml` under `requires` with its exact ORD ID from the generated asset
- [x] After MCP assets are generated, create `mcp-mock.json` using the `mcp-mock-config` skill (required before tests can run)

---

## Testing

> See [guidelines-agent-python.md](../guidelines-agent-python.md) for Python testing setup and patterns.

- [x] `conftest.py` only sets `IBD_TESTING=true`
- [x] Write unit test for `search_products` tool: mock MCP response, assert correct fields are returned for a valid product name query; run immediately after writing
- [x] Write unit test for `get_product_details` tool: mock MCP response with a full product record, assert all required fields (product number, description, group, UoM, type) are present; run immediately after writing
- [x] Write unit test for graceful error handling: mock MCP returning empty results, assert agent response informs the user the product was not found; run immediately after writing
- [x] Write unit test for out-of-scope query handling: send a pricing question, assert the agent declines and suggests where to find pricing info; run immediately after writing
- [x] Write one integration test: end-to-end agent flow — submit a natural language product question, mock LLM and MCP tools, assert a correct structured product answer is returned
- [x] Run `pytest` from `assets/product-master-data-agent/` (no args) — if coverage < 70%, add tests until threshold met
- [x] Run `pytest` again from `assets/product-master-data-agent/` (no args) to generate final `test_report.json`
- [x] Verify `test_report.json` exists in `assets/product-master-data-agent/`
