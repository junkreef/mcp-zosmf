# `mcp_zosmf` - AI Agent Toolset for z/OSMF

## 1. Project Overview

This project's core objective is to empower AI agents with the capability to operate a z/OS mainframe autonomously.

It achieves this by wrapping the rich suite of z/OSMF REST APIs as MCP Tools, exposing complex mainframe operations as simple, structured Python functions. The primary target users are AI Agents operating within the `FastMCP` framework.

The system aims to provide tools for manipulating various z/OS resources, covering areas such as (but not limited to) Job Operations, Data and File Operations, and System Operations.

## 2. Build and Test Commands

*   **Environment Setup:** This project uses `uv` for dependency management. To install all required dependencies, run:
    ```bash
    uv sync
    ```

*   **Running Tests:** The project has a comprehensive test suite using `pytest`. To run all tests and ensure the project's integrity, use the following command:
    ```bash
    uv run pytest
    ```

## 3. Testing Procedures

The typical workflow for adding a new tool (and its tests) is as follows:
1.  **Identify the API:** Locate the target z/OSMF REST API endpoint and understand its request/response structure.
2.  **Implement the Method:** Add a new method to the appropriate Tool class in the `src/mcp_zosmf/tools/` directory.
3.  **Define the Schema:** If the API returns a JSON object or array, create a corresponding Pydantic model in `src/mcp_zosmf/schemas.py` to ensure response validation.
4.  **Create Tests:** Add a new test file or update an existing one in the `tests/` directory. The tests must cover both successful execution and relevant error/edge cases (e.g., API errors, validation errors, empty responses). Use mocking to isolate the tool from the live API.

## 4. Coding Style Guidelines

To ensure code consistency and readability, this project adheres to the following guidelines:

*   **PEP 8:** All Python code should follow the PEP 8 style guide.
*   **Type Hinting:** All function signatures and variables should include type hints. This is critical for both static analysis and for AI agents to understand the data types involved.
*   **Docstrings:** All modules, classes, and functions should have clear and concise docstrings explaining their purpose.
*   **Clarity over Brevity:** Write clear, self-documenting code. Prefer descriptive variable names (e.g., `job_list`) over short, ambiguous ones (e.g., `j_list`).
*   **Conventional Commits:** All commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

## 5. Security Considerations

As this project provides tools to operate on a z/OS mainframe, security is of utmost importance.

*   **Credential Management:** The `ZosmfClient` requires z/OSMF credentials. These are sensitive and **must not** be hardcoded in the source code. They should be passed securely at runtime from a secure source (e.g., environment variables, a secret manager) into the `FastMCP` application.
*   **Command Execution:** The `ConsoleTools` provides the ability to issue arbitrary system commands. While the AI agent is considered a trusted actor, it is crucial that the logic generating these commands is sound and does not inadvertently create dangerous commands based on malformed inputs.
*   **Principle of Least Privilege:** The z/OSMF user account associated with these tools should have the minimum set of permissions required to perform its intended functions. Avoid using highly privileged accounts unless absolutely necessary.

## 6. Design Details (Reference)

*   **Overall Architecture:** A Python-based plugin for the `FastMCP` framework, acting as a translation layer between an AI agent's intent and z/OSMF API calls.
*   **Key Components:**
    *   **`ZosmfClient`:** A centralized client responsible for all HTTP communication, authentication, token management, and low-level error handling.
    *   **Tool Classes (e.g., `JobsTools`, `FilesTools`, `ConsoleTools`):** Group related functions and expose them as tools to the `FastMCP` application.
    *   **Pydantic Schemas:** Define the data contracts for all API responses, ensuring type safety and data integrity. This structured data is essential for AI agents to reliably interpret tool outputs.
*   **Technology Stack:**
    *   **Language:** Python
    *   **Dependencies:** `uv` (management), `pytest` (testing), `requests` (HTTP), `pydantic` (validation), `fastmcp` (framework).

---
