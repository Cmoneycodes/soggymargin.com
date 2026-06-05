#!/usr/bin/env python3
import sys
from pathlib import Path
from datetime import datetime
import pypdf
import pdfplumber

def pdf_to_markdown(pdf_path: Path, max_pages: int = 50) -> str:
    """Extract text and tables from PDF into Markdown format."""
    if not pdf_path.exists():
        return f"# Error\n\nFile not found: {pdf_path}\n\n"
    
    md_parts = [f"# Document: {pdf_path.name}", 
                f"**Path:** `{pdf_path}`",
                f"**Processed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"**Source PDF Size:** {pdf_path.stat().st_size / 1024:.1f} KB\n",
                "---\n"]
    
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        num_pages = len(reader.pages)
        md_parts.append(f"**Pages:** {num_pages} (extracting up to {max_pages})\n")
        
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page_num in range(min(num_pages, max_pages)):
                md_parts.append(f"## Page {page_num + 1}")
                
                # Text
                page_text = reader.pages[page_num].extract_text(extraction_mode="layout") or "No text extracted."
                if page_text.strip():
                    md_parts.append(page_text.strip())
                    md_parts.append("")
                
                # Tables - limited to avoid bloat
                try:
                    pl_page = pdf.pages[page_num]
                    tables = pl_page.extract_tables()
                    for t_idx, table in enumerate(tables):
                        if table and len(table) > 1:  # has content
                            md_parts.append(f"### Table {t_idx+1}")
                            # Convert to MD table
                            header = table[0]
                            if header:
                                md_parts.append("| " + " | ".join(str(h or '').strip() for h in header) + " |")
                                md_parts.append("| " + " | ".join("---" for _ in header) + " |")
                                for row in table[1:]:
                                    if row:
                                        md_parts.append("| " + " | ".join(str(cell or '').strip() for cell in row) + " |")
                            md_parts.append("")
                except Exception as table_err:
                    md_parts.append(f"*Table extraction note: {table_err}*")
                
                md_parts.append("---")
                md_parts.append("")
    except Exception as e:
        md_parts.append(f"**Extraction failed:** {str(e)}")
    
    md_parts.append("\n*End of {pdf_path.name}*")
    return "\n\n".join(md_parts)

if __name__ == "__main__":
    # PDFs to process - small/relevant ones only
    base_dir = Path(r"C:\Users\colli\AppData\Local\hermes\hermes-agent")
    pdf_list = [
        base_dir / "docs" / "hermes-kanban-v1-spec.pdf",
        base_dir / "skills" / "research" / "research-paper-writing" / "templates" / "icml2026" / "icml_numpapers.pdf",
        base_dir / "skills" / "research" / "research-paper-writing" / "templates" / "colm2025" / "colm2025_conference.pdf",
    ]
    
    combined = ["# Consolidated PDF Extraction Report\n"]
    combined.append(f"**Generation Time:** {datetime.now().isoformat()}")
    combined.append(f"**Documents Processed:** {len(pdf_list)}")
    combined.append("**Purpose:** Provides clean Markdown version of PDF contents for use in notes, Obsidian/Zanus vaults, RAG, or analysis.\n")
    combined.append("---\n")
    
    for pdf_path in pdf_list:
        print(f"Processing: {pdf_path.name}")
        doc_md = pdf_to_markdown(pdf_path)
        combined.append(doc_md)
        combined.append("\n" + "=" * 100 + "\n\n")
    
    output_file = Path("combined_pdfs_to_markdown.md")
    output_file.write_text("\n".join(combined), encoding="utf-8")
    print(f"\n✅ Successfully created large Markdown file: {output_file.absolute()}")
    print(f"Approximate size: {output_file.stat().st_size // 1024} KB")
    print("\nYou can now use this file directly or import into Zanus/Obsidian.")
