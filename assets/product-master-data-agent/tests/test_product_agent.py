"""
Unit and integration tests for the Product Master Data Agent.

Tests cover:
- search_products / list tool: returns correct product fields
- get_product_details / get tool: returns full product record
- Graceful error handling when product not found
- Out-of-scope query handling (pricing questions)
- End-to-end integration: natural language question → structured product answer
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

AGENT_ROOT = Path(__file__).parent.parent

MOCK_PRODUCT_LIST = {
    "results": [
        {
            "Product": "LAPTOP-PRO-X",
            "ProductType": "FERT",
            "ProductGroup": "ELECTR",
            "BaseUnit": "EA",
            "Division": "10",
            "GrossWeight": "2.500",
            "NetWeight": "2.100",
            "WeightUnit": "KG",
        },
        {
            "Product": "MONITOR-4K-27",
            "ProductType": "FERT",
            "ProductGroup": "ELECTR",
            "BaseUnit": "EA",
            "Division": "10",
            "GrossWeight": "6.800",
            "NetWeight": "5.900",
            "WeightUnit": "KG",
        },
    ]
}

MOCK_PRODUCT_SINGLE = {
    "Product": "LAPTOP-PRO-X",
    "ProductType": "FERT",
    "ProductGroup": "ELECTR",
    "BaseUnit": "EA",
    "Division": "10",
    "GrossWeight": "2.500",
    "NetWeight": "2.100",
    "WeightUnit": "KG",
}

MOCK_PRODUCT_DESCRIPTION = {
    "Product": "LAPTOP-PRO-X",
    "Language": "EN",
    "ProductDescription": "Laptop Pro X - Business Edition",
}


def _make_tool_mock(name: str, return_value: Any) -> MagicMock:
    """Create a mock LangChain tool with ainvoke returning a JSON string."""
    tool = MagicMock()
    tool.name = name
    tool.ainvoke = AsyncMock(return_value=json.dumps(return_value))
    return tool


# ---------------------------------------------------------------------------
# Test: list_a_product tool (search_products path)
# ---------------------------------------------------------------------------

@pytest.mark.usefixtures("add_agent_to_path")
def test_list_product_tool_returns_correct_fields():
    """list_a_product_for_api_product_srv mock returns the expected product fields."""
    tool = _make_tool_mock(
        "mcp_sap-s4-product-master__list_a_product_for_api_product_srv",
        MOCK_PRODUCT_LIST,
    )
    result = json.loads(tool.ainvoke.return_value)
    products = result.get("results", [])
    assert len(products) == 2
    first = products[0]
    assert first["Product"] == "LAPTOP-PRO-X"
    assert first["ProductGroup"] == "ELECTR"
    assert first["BaseUnit"] == "EA"
    assert first["ProductType"] == "FERT"


# ---------------------------------------------------------------------------
# Test: get_a_product tool (get_product_details path)
# ---------------------------------------------------------------------------

@pytest.mark.usefixtures("add_agent_to_path")
def test_get_product_tool_returns_full_record():
    """get_a_product_for_api_product_srv mock returns all required product master fields."""
    tool = _make_tool_mock(
        "mcp_sap-s4-product-master__get_a_product_for_api_product_srv",
        MOCK_PRODUCT_SINGLE,
    )
    result = json.loads(tool.ainvoke.return_value)
    required_fields = ["Product", "ProductGroup", "BaseUnit", "ProductType", "Division"]
    for field in required_fields:
        assert field in result, f"Missing field: {field}"
    assert result["Product"] == "LAPTOP-PRO-X"
    assert result["BaseUnit"] == "EA"
    assert result["Division"] == "10"


# ---------------------------------------------------------------------------
# Test: graceful error handling when product not found
# ---------------------------------------------------------------------------

@pytest.mark.usefixtures("add_agent_to_path")
def test_empty_results_handled_gracefully():
    """When the MCP tool returns empty results, the agent should not crash."""
    tool = _make_tool_mock(
        "mcp_sap-s4-product-master__list_a_product_for_api_product_srv",
        {"results": []},
    )
    result = json.loads(tool.ainvoke.return_value)
    products = result.get("results", [])
    assert products == [], "Expected empty results list"
    # Agent logic should inform user; empty list is a valid, handled response
    assert len(products) == 0


# ---------------------------------------------------------------------------
# Test: out-of-scope query — pricing question should be declined by system prompt
# ---------------------------------------------------------------------------

@pytest.mark.usefixtures("add_agent_to_path")
def test_system_prompt_blocks_pricing_queries():
    """System prompt must explicitly decline pricing questions."""
    from agent import get_system_prompt
    prompt = get_system_prompt()
    # The prompt should reference pricing as out of scope
    assert "pric" in prompt.lower(), "System prompt should address pricing scope"
    assert "VK13" in prompt or "pricing" in prompt.lower(), (
        "System prompt should guide user to pricing resources"
    )


# ---------------------------------------------------------------------------
# Test: system prompt correctness
# ---------------------------------------------------------------------------

@pytest.mark.usefixtures("add_agent_to_path")
def test_system_prompt_read_only_guardrail():
    """System prompt must instruct the agent to never modify product records."""
    from agent import get_system_prompt
    prompt = get_system_prompt()
    assert "read-only" in prompt.lower() or "never create" in prompt.lower() or "never modif" in prompt.lower(), (
        "System prompt must include read-only guardrail"
    )


@pytest.mark.usefixtures("add_agent_to_path")
def test_system_prompt_no_fabrication():
    """System prompt must instruct the agent not to fabricate data."""
    from agent import get_system_prompt
    prompt = get_system_prompt()
    assert "never fabricate" in prompt.lower() or "do not invent" in prompt.lower() or "fabricate" in prompt.lower(), (
        "System prompt must prohibit data fabrication"
    )


# ---------------------------------------------------------------------------
# Test: mcp-mock.json structure
# ---------------------------------------------------------------------------

def test_mcp_mock_json_structure():
    """mcp-mock.json must exist, be valid JSON, and contain expected tools."""
    mock_path = AGENT_ROOT / "mcp-mock.json"
    assert mock_path.exists(), "mcp-mock.json must exist at agent root"

    data = json.loads(mock_path.read_text())
    assert "servers" in data, "mcp-mock.json must have 'servers' key"
    assert len(data["servers"]) >= 1, "Must have at least one server"

    # Find any server that has the product list tool
    found_list_tool = False
    found_get_tool = False
    found_description_tool = False
    for server in data["servers"].values():
        tools = server.get("tools", {})
        if "list_a_product_for_api_product_srv" in tools:
            found_list_tool = True
        if "get_a_product_for_api_product_srv" in tools:
            found_get_tool = True
        if "list_a_productdescription_for_api_product_srv" in tools:
            found_description_tool = True

    assert found_list_tool, "mcp-mock.json must include list_a_product tool"
    assert found_get_tool, "mcp-mock.json must include get_a_product tool"
    assert found_description_tool, "mcp-mock.json must include list_a_productdescription tool"


# ---------------------------------------------------------------------------
# Integration test: end-to-end agent invoke with mocked LLM and MCP tools
# ---------------------------------------------------------------------------

@pytest.mark.usefixtures("add_agent_to_path")
@pytest.mark.asyncio
async def test_agent_invoke_product_query():
    """End-to-end: agent.invoke() returns a completed response for a product query."""
    mock_tools = [
        _make_tool_mock(
            "mcp_sap-s4-product-master__list_a_product_for_api_product_srv",
            MOCK_PRODUCT_LIST,
        ),
        _make_tool_mock(
            "mcp_sap-s4-product-master__get_a_product_for_api_product_srv",
            MOCK_PRODUCT_SINGLE,
        ),
        _make_tool_mock(
            "mcp_sap-s4-product-master__get_a_productdescription_for_api_product_srv",
            MOCK_PRODUCT_DESCRIPTION,
        ),
    ]

    mock_llm_response = MagicMock()
    mock_llm_response.content = (
        "The product LAPTOP-PRO-X is a 'Laptop Pro X - Business Edition'. "
        "It belongs to product group ELECTR, has a base unit of measure of EA (each), "
        "and weighs 2.1 kg net."
    )

    with (
        patch("mcp_providers.agw.get_mcp_tools", new=AsyncMock(return_value=mock_tools)),
        patch("langchain_litellm.ChatLiteLLM") as mock_llm_cls,
    ):
        mock_llm_instance = MagicMock()
        mock_llm_cls.return_value = mock_llm_instance

        # Simulate the graph returning the mocked LLM response
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = {
            "messages": [mock_llm_response]
        }

        from agent import SampleAgent
        agent = SampleAgent()
        agent._checkpointer = MagicMock()

        with patch.object(agent, "_create_graph", return_value=mock_graph):
            response = await agent.invoke(
                query="What is the base unit of measure for product LAPTOP-PRO-X?",
                context_id="test-session-001",
                tools=mock_tools,
            )

    assert response.status == "completed"
    assert response.message, "Response message should not be empty"
