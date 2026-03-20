import os
from pathlib import Path
from docling.document_converter import DocumentConverter

def process_university_kb(input_folder: str, output_folder: str):
    converter = DocumentConverter()

    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"🚀 Starting conversion for files in: {input_path}")

    for pdf_file in input_path.glob("*.pdf"):
        try:
            print(f"📄 Processing: {pdf_file.name}...")

            result = converter.convert(pdf_file)

            markdown_content = result.document.export_to_markdown()

            output_file = output_path / f"{pdf_file.stem}.md"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            print(f"✅ Saved to: {output_file.name}")

        except Exception as e:
            print(f"❌ Error processing {pdf_file.name}: {e}")

if __name__ == "__main__":
    SOURCE_DIR = "./raw_policies"
    OUTPUT_DIR = "./processed_kb"

    process_university_kb(SOURCE_DIR, OUTPUT_DIR)