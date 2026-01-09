from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from pydantic import Field

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}


@mcp.tool(
    name="read_document_contents",
    description="Reads the contents of a document given its ID.",
)
def read_document(
    doc_id: str = Field(description="The ID of the document to read."),
) -> str:
    """Reads the contents of a document given its ID."""
    if doc_id not in docs:
        raise ValueError(f"The document {doc_id} does not exist.")
    return docs[doc_id]


@mcp.tool(
    name="edit_document_contents",
    description="Edits the contents of a document given its ID by replacing old string in content with a new string",
)
def edit_document(
    doc_id: str = Field(description="The ID of the document to edit."),
    new_str: str = Field(description="The new string to write to the document."),
    old_str: str = Field(
        description="The old string to remove to the document. Must match exactly."
    ),
) -> str:
    """Edits the contents of a document given its ID."""
    if doc_id not in docs:
        raise ValueError(f"The document {doc_id} does not exist.")
    content = docs[doc_id]
    if old_str not in content:
        raise ValueError(f"The string '{old_str}' was not found in the document.")
    updated_content = content.replace(old_str, new_str)
    docs[doc_id] = updated_content
    return updated_content


@mcp.resource(
    uri := "docs://documents",
    mime_type="application/json",
)
def list_document_ids() -> list[str]:
    """Returns a list of all document IDs."""
    return list(docs.keys())


@mcp.resource(
    uri="docs://documents/{doc_id}",
    mime_type="text/plain",
)
def read_document(doc_id: str) -> str:
    """Returns the contents of a particular document given its ID."""
    if doc_id not in docs:
        raise ValueError(f"The document {doc_id} does not exist.")
    return docs[doc_id]


@mcp.prompt(
    name="format",
    description="Rewrite a document in markdown format.",
)
def format_document_prompt(
    doc_id: str = Field(description="Id of the document to format"),
) -> list[base.Message]:
    """Prompt to reformat a document in markdown format."""
    prompt = f"""
Your goal is to reformat a document to be written with markdown syntax.

The id of the document you need to reformat is:

{doc_id}


Add in headers, bullet points, tables, etc as necessary. Feel free to add in structure.
Use the 'edit_document' tool to edit the document. After the document has been reformatted...
"""

    return [base.UserMessage(prompt)]


if __name__ == "__main__":
    mcp.run(transport="stdio")
