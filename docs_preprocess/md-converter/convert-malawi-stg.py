import fitz
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PictureDescriptionVlmEngineOptions,
    TableFormerMode,
    TableStructureOptions,
    ThreadedPdfPipelineOptions,
)
from docling.datamodel.vlm_engine_options import ApiVlmEngineOptions, VlmEngineType
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.threaded_standard_pdf_pipeline import ThreadedStandardPdfPipeline


def main():
    source = "pdf/malawi-stg-cleaned.pdf"  # file path or URL

    temp_doc = fitz.open(source)
    total_pages = temp_doc.page_count
    # total_pages = 45
    temp_doc = None

    pipeline_options = ThreadedPdfPipelineOptions(
        accelerator_options=AcceleratorOptions(
            device=AcceleratorDevice.AUTO,
        ),
        ocr_batch_size=4,
        layout_batch_size=4,
        table_batch_size=4,
        do_ocr=False,
        do_table_structure=True,
        table_structure_options=TableStructureOptions(
            mode=TableFormerMode.ACCURATE
        ),
        do_picture_description=False,
        picture_description_options=PictureDescriptionVlmEngineOptions.from_preset(
            preset_id="granite_vision",
            engine_options=ApiVlmEngineOptions(
                engine_type=VlmEngineType.API_LMSTUDIO,
                url="http://localhost:1234/v1/chat/completions",
            ),
        ),
        enable_remote_services=True,
        queue_max_size=10
    )
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=ThreadedStandardPdfPipeline,
                pipeline_options=pipeline_options,
            )
        }
    )

    doc = None

    for i in range (1, total_pages, 10):
        page_range = (i if i == 1 else i + 1, min(i + 10, total_pages))
        print(f"Processing page range {page_range}...")

        doc = converter.convert(source, page_range=(i, i + 10)).document

        md = doc.export_to_markdown()

        print("Writing markdown to malawi-stg.md...")

        if md:
            with open("markdowns/malawi-stg.md", "a", encoding="utf-8") as f:
                f.write(md)

        print(f"Done processing page range {page_range}.")

if __name__ == "__main__":
    main()
