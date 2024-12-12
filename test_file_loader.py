import os
from mindsdb.integrations.utilities.rag.loaders.file_loader import FileLoader

# Helper function to check if a file exists
def file_exists(filepath):
    return os.path.exists(filepath)

def test_load_pdf():
    pdf_path = './tests/integrations/utilities/rag/data/test.pdf'
    
    # Ensure the file exists before attempting to load it
    assert file_exists(pdf_path), f"File not found: {pdf_path}"
    
    loader = FileLoader(pdf_path)
    docs = loader.load()
    # Each page is a doc.
    assert len(docs) == 3, f"Expected 3 docs, got {len(docs)}"
    assert 'THE CASE FOR MACHINE LEARNING' in docs[0].page_content
    assert 'INTRODUCTION' in docs[1].page_content
    assert 'THE CASE FOR \nDEMOCRATIZING \nMACHINE LEARNING' in docs[2].page_content

def test_load_csv():
    csv_path = './tests/integrations/utilities/rag/data/movies.csv'
    
    # Ensure the file exists before attempting to load it
    assert file_exists(csv_path), f"File not found: {csv_path}"
    
    loader = FileLoader(csv_path)
    docs = loader.load()
    # Each row is a doc.
    assert len(docs) == 10, f"Expected 10 docs, got {len(docs)}"
    assert 'Toy Story' in docs[0].page_content
    assert 'GoldenEye' in docs[9].page_content

def test_load_html():
    html_path = './tests/integrations/utilities/rag/data/test.html'
    
    # Ensure the file exists before attempting to load it
    assert file_exists(html_path), f"File not found: {html_path}"
    
    loader = FileLoader(html_path)
    docs = loader.load()
    assert len(docs) == 1, f"Expected 1 doc, got {len(docs)}"
    assert 'Some intro text about Foo' in docs[0].page_content

def test_load_md():
    md_path = './mindsdb/integrations/handlers/langchain_handler/README.md'
    
    # Ensure the file exists before attempting to load it
    assert file_exists(md_path), f"File not found: {md_path}"
    
    loader = FileLoader(md_path)
    docs = loader.load()
    assert len(docs) == 1, f"Expected 1 doc, got {len(docs)}"
    assert 'This documentation describes the integration of MindsDB with LangChain' in docs[0].page_content

def test_load_text():
    text_path = './tests/integrations/utilities/rag/data/test.txt'
    
    # Ensure the file exists before attempting to load it
    assert file_exists(text_path), f"File not found: {text_path}"
    
    loader = FileLoader(text_path)
    docs = loader.load()
    assert len(docs) == 1, f"Expected 1 doc, got {len(docs)}"
    assert 'This is a test plaintext file' in docs[0].page_content
