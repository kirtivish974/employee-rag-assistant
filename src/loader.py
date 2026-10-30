from pathlib import Path

from langchain_community.document_loaders import (
    DirectoryLoader,
    UnstructuredMarkdownLoader,
    BSHTMLLoader,
    PyPDFLoader
)
from langchain_core.documents import Document

# Project root
HANDBOOK_DIR = Path("handbook")

# Files that should not enter the CivicActions Q&A corpus
EXCLUDED_FILES = {
    "README.md",
    "CONTRIBUTING.md",
    "LICENSE.md",
    "README_18f.md",
    "aloha-etams-reconciliation-feature.md",
    "gsa-tools-equipment-and-transit.md",
}

# Markers that identify the CivicActions section in benefits.md
START_MARKER = "<!-- TODO: Begin CA:Handbook -->"
END_MARKER = "<!-- TODO: END CA:Handbook -->"


def clean_benefits_document(doc):
    """Keep only the CivicActions section of benefits.md."""

    source_path = Path(doc.metadata["source"])

    # Read the original Markdown file to preserve exact marker boundaries
    raw_text = source_path.read_text(encoding="utf-8")

    if START_MARKER not in raw_text or END_MARKER not in raw_text:
        raise ValueError(
            f"CivicActions section markers missing in: {source_path}"
        )

    start = raw_text.index(START_MARKER) + len(START_MARKER)
    end = raw_text.index(END_MARKER, start)

    cleaned_text = raw_text[start:end].strip()

    if not cleaned_text:
        raise ValueError(
            f"CivicActions section is empty in: {source_path}"
        )

    metadata = dict(doc.metadata)
    metadata["policy_scope"] = "CivicActions"
    metadata["section"] = "Employee Benefits"

    return Document(
        page_content=cleaned_text,
        metadata=metadata
    )


# Load Markdown documents
md_docs = DirectoryLoader(
    str(HANDBOOK_DIR),
    glob="**/*.md",
    loader_cls=UnstructuredMarkdownLoader,
    exclude=[
        "**/README.md",
        "**/CONTRIBUTING.md",
        "**/LICENSE.md",
        "**/README_18f.md",
        "**/aloha-etams-reconciliation-feature.md",
        "**/gsa-tools-equipment-and-transit.md",
    ]
).load()

# Clean the mixed CivicActions/GSA benefits document
benefits_found = False

for i, doc in enumerate(md_docs):
    if Path(doc.metadata["source"]).name == "benefits.md":
        md_docs[i] = clean_benefits_document(doc)
        benefits_found = True

if not benefits_found:
    raise ValueError("benefits.md was not loaded. Check the handbook directory.")

# Load HTML documents
html_docs = DirectoryLoader(
    str(HANDBOOK_DIR),
    glob="**/*.html",
    loader_cls=BSHTMLLoader
).load()

# Load PDF documents
pdf_docs = DirectoryLoader(
    str(HANDBOOK_DIR),
    glob="**/*.pdf",
    loader_cls=PyPDFLoader,
    exclude=[
        "**/setting_up_otp_for_remote_access.pdf",
        "**/standard-ethical-conduct.pdf",
    ]
).load()

# Combine documents
all_docs = md_docs + html_docs + pdf_docs

print("Markdown documents:", len(md_docs))
print("HTML documents:", len(html_docs))
print("PDF documents/pages:", len(pdf_docs))
print("Total documents/pages:", len(all_docs))

# Verify excluded files
for doc in all_docs:
    source = Path(doc.metadata["source"])

    if source.name in EXCLUDED_FILES:
        raise ValueError(f"Excluded document was loaded: {source}")

# Verify benefits document contains only the CivicActions section
benefits_doc = next(
    doc for doc in md_docs
    if Path(doc.metadata["source"]).name == "benefits.md"
)

assert "Holidays" in benefits_doc.page_content
assert "Paid Time Off" in benefits_doc.page_content
assert START_MARKER not in benefits_doc.page_content
assert END_MARKER not in benefits_doc.page_content

print("Benefits document filtering: PASSED")
print("CivicActions employee-policy filtering: PASSED")