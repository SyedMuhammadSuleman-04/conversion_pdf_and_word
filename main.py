import streamlit as st
import os
from io import BytesIO
from pdf2docx import Converter
from docx import Document
from fpdf import FPDF

st.set_page_config(page_title="File Converter", layout='wide')
st.title('📄 File Converter')
st.write('🔄 Convert PDF to Word and Word to PDF with ease!')

# Ensure temp directory exists
os.makedirs("temp", exist_ok=True)

uploaded_files = st.file_uploader('Upload your files (PDF or Word):', type=["pdf", "docx"], accept_multiple_files=True)

if uploaded_files:
    st.write("✅ Files uploaded successfully!")
    for file in uploaded_files:
        st.write(f"Processing file: {file.name}")
        file_ext = os.path.splitext(file.name)[-1].lower()
        
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file.size/1024:.2f} KB")

        if file_ext == ".pdf":
            conversion_type = "Word"
        elif file_ext == ".docx":
            conversion_type = "PDF"
        else:
            st.error(f"Unsupported file format: {file_ext}")
            continue

        if st.button(f"Convert {file.name} to {conversion_type}"):
            buffer = BytesIO()
            temp_file_path = os.path.join("temp", file.name)
            output_file = file.name.replace(file_ext, ".docx" if file_ext == ".pdf" else ".pdf")
            output_file_path = os.path.join("temp", output_file)

            try:
                with open(temp_file_path, "wb") as f:
                    f.write(file.getbuffer())
                st.write(f"File saved to: {temp_file_path}")
            except Exception as e:
                st.error(f"Error saving file: {e}")
                continue

            if file_ext == ".pdf":
                try:
                    pdf_converter = Converter(temp_file_path)
                    pdf_converter.convert(output_file_path)
                    pdf_converter.close()
                    with open(output_file_path, "rb") as out_file:
                        buffer.write(out_file.read())
                    mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                except Exception as e:
                    st.error(f"Error converting PDF to Word: {e}")
                    continue
            
            elif file_ext == ".docx":
                try:
                    doc = Document(temp_file_path)
                    pdf = FPDF()
                    pdf.set_auto_page_break(auto=True, margin=15)
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    for para in doc.paragraphs:
                        text = para.text.encode('latin-1', 'replace').decode('latin-1')
                        pdf.multi_cell(0, 10, text)
                    pdf.output(output_file_path)
                    with open(output_file_path, "rb") as out_file:
                        buffer.write(out_file.read())
                    mime_type = "application/pdf"
                except Exception as e:
                    st.error(f"Error converting Word to PDF: {e}")
                    continue
            
            buffer.seek(0)
            st.download_button(
                label=f"⬇️ Download {output_file}",
                data=buffer,
                file_name=output_file,
                mime=mime_type
            )

            os.remove(temp_file_path)
            os.remove(output_file_path)

            st.success(f"✅ {file.name} converted successfully to {conversion_type}!")
else:
    st.warning("Please upload at least one PDF or Word file.")
