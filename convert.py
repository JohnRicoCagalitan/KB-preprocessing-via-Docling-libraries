import os
import gc
from pathlib import Path
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from pypdf import PdfReader, PdfWriter

def process_heavy_pdfs_isolated(input_folder, output_folder):
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
            reader = PdfReader(pdf_file)
            total_pages = len(reader.pages)
            full_markdown = []
            
            # 2. Process every page by creating a temporary 1-page PDF
            for i in range(total_pages):
                page_num = i + 1
                temp_filename = f"temp_page_{page_num}.pdf"
                
                try:
                    # Create a 1-page PDF file
                    writer = PdfWriter()
                    writer.add_page(reader.pages[i])
                    with open(temp_filename, "wb") as f:
                        writer.write(f)
                    
                    # Convert the 1-page file
                    result = converter.convert(temp_filename)
                    page_md = result.document.export_to_markdown()
                    full_markdown.append(page_md)
                    
                    print(f"  Page {page_num}/{total_pages} successful.")
                    
                    # Cleanup after page
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
                    del result
                    gc.collect()
                    
                except Exception as page_err:
                    print(f"  Skipped Page {page_num} due to error: {page_err}")
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
            
            # 3. Save the final combined Markdown
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
    process_heavy_pdfs_isolated(SOURCE_DIR, OUTPUT_DIR)