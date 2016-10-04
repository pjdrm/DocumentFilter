import os

def get_doc_type(docFileName):
    docFileName = docFileName.replace("_processed_annotated", "")
    with open(os.path.join(docFileName)) as f:
        a = f.readline()
        return f.readline()[1:-1]
    
def add_doc_type(docsDir, rootOriginalDocs):
    for file in os.listdir(docsDir):
        if "_v" in file:
            continue
        doc_type = get_doc_type(os.path.join(rootOriginalDocs, docsDir.split("/")[-1], file[4:]))
        os.rename(os.path.join(docsDir, file), os.path.join(docsDir, file.replace(".txt", "_" + doc_type + ".txt")))
        
def run(rootDocsDir, rootOriginalDocs):
    for dir in os.listdir(rootDocsDir):
        add_doc_type(os.path.join(rootDocsDir, dir), rootOriginalDocs)
        
run("/home/pjdrm/Desktop/docs_annoted", "/home/pjdrm/Desktop/docs_txt")
    