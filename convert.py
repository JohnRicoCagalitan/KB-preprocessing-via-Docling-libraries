import os
import gc
from pathlib import Path
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from pypdf import PdfReader

def process_heavy_pdfs(input_folder, output_folder):
    # 1. Configuration
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True 
    
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Starting conversion for files in: {input_path}")
    
    for pdf_file in input_path.glob("*.pdf"):
        try:
            print(f"Processing: {pdf_file.name}")
            
            # 2. Get the total number of pages
            reader = PdfReader(pdf_file)
            total_pages = len(reader.pages)
            print(f"Found {total_pages} pages. Converting sequentially...")
            
            full_markdown = []
            
            # 3. Process every page individually
            for page_num in range(1, total_pages + 1):
                try:
                    # Isolate processing to a single page
                    result = converter.convert(pdf_file, page_range=[page_num])
                    page_md = result.document.export_to_markdown()
                    full_markdown.append(page_md)
                    print(f"  Page {page_num}/{total_pages} successful.")
                    
                    # 4. Force Memory Cleanup
                    del result
                    gc.collect()
                    
                except Exception as page_err:
                    print(f"  Skipped Page {page_num} due to error: {page_err}")
                    full_markdown.append(f"\n> [MISSING CONTENT: Page {page_num} failed to process]\n")

            # 5. Save the final Markdown file
            output_file = output_path / f"{pdf_file.stem}.md"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"--- \nsource: {pdf_file.name}\n---\n\n")
                f.write("\n\n".join(full_markdown))
                
            print(f"File saved to: {output_file.name}\n")
            
        except Exception as e:
            print(f"Failed to read {pdf_file.name}: {e}")

if __name__ == "__main__":
    SOURCE_DIR = "./raw_policies"
    OUTPUT_DIR = "./processed_kb"
    process_heavy_pdfs(SOURCE_DIR, OUTPUT_DIR)