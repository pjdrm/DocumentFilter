'''
Created on Aug 25, 2016

@author: Pedro Mota
'''
import os
from shutil import copyfile
import ntpath
import shutil


def create_labels(files_list, outFile):
    str_labels = ""
    topic = 0
    docId = 0
    for file_path in files_list:
        segs = getSegments(file_path)
        for seg in segs:
            str_labels += str(topic) + " " + str(docId) + "::" + seg + "\n"
            topic += 1
        docId += 1
            
    with open(outFile, "w+") as f:
        f.write(str_labels[:-1])
            
def getSegments(file_path):
    segs = []
    with open(file_path, encoding="utf8", errors="ignore") as f:
        lines = f.readlines()[1:]
        segStart = 0
        segEnd = 0
        for lin in lines:
            if lin.startswith("=========="):
                segs.append(str(segStart) + "-" + str(segEnd-1))
                segStart = segEnd
            else:
                segEnd += 1
    return segs

def remove_boundaries(file_list):
    for file_path in file_list:
        with open(file_path, encoding="utf8", errors="ignore") as f:
            str = f.read()
        str = str.replace("==========\n", "").replace("==========", "")
        with open(file_path, "w", encoding="utf8", errors="ignore") as f:
            f.write(str)
            
def get_files(otherDocsDir, file_type):
    if file_type == "all":
        return os.listdir(otherDocsDir)
    
    dir = otherDocsDir.replace("docs_annoted", "docs_txt")
    files_list = []
    for f_path in os.listdir(otherDocsDir):
        f_path2 = f_path.replace("_processed_annotated", "")
        if "_v" in f_path2:
            type = "video"
        else:
            f_path2 = f_path2[4:]
            with open(os.path.join(dir, f_path2), encoding="utf8", errors="ignore") as f:
                f.readline()
                type = f.readline()[1:-1]
        if type == file_type:
            files_list.append(f_path)
    return files_list
    
def run(originalRefPath, otherDocsDir, outDir, file_type):
    if os.path.exists(outDir):
        shutil.rmtree(outDir)
    os.mkdir(outDir)
    new_files = []
    origFile = os.listdir(otherDocsDir)[0].split("_")[0] + ".ref"
    filesList = [os.path.join(originalRefPath, origFile)]
    doc_set_id = "000."
    print(origFile + " " + doc_set_id + "0")
    new_files.append(os.path.join(outDir, doc_set_id + "0"))
    with open(os.path.join(outDir, doc_set_id + "0"), "w+") as f:
            f.write("")
    copyfile(filesList[0], os.path.join(outDir, doc_set_id + "0"))
    
    for doc_id, f_path in enumerate(get_files(otherDocsDir, file_type)):
        doc_id += 1
        full_path = os.path.join(otherDocsDir, f_path)
        filesList.append(full_path)
        new_file = os.path.join(outDir, doc_set_id + str(doc_id))
        print(f_path + " " + doc_set_id + str(doc_id))
        new_files.append(new_file)
        with open(new_file, "w+") as f:
            f.write("")
        copyfile(full_path, new_file)
    create_labels(filesList, os.path.join(outDir, "000.label"))
    remove_boundaries(new_files)
    
def run_type_pure(originalRefPath, otherDocsDir, outDir, file_type):
    if os.path.exists(outDir):
        shutil.rmtree(outDir)
    os.mkdir(outDir)
    new_files = []
    filesList = []
    doc_id = 0
    doc_set_id = "000."
    if file_type == "video":
        doc_id += 1
        origFile = os.listdir(otherDocsDir)[0].split("_")[0] + ".ref"
        filesList = [os.path.join(originalRefPath, origFile)]
        print(origFile + " " + doc_set_id + "0")
        new_files.append(os.path.join(outDir, doc_set_id + "0"))
        with open(os.path.join(outDir, doc_set_id + "0"), "w+") as f:
                f.write("")
        copyfile(filesList[0], os.path.join(outDir, doc_set_id + "0"))
    
    for f_path in get_files(otherDocsDir, file_type):
        full_path = os.path.join(otherDocsDir, f_path)
        filesList.append(full_path)
        new_file = os.path.join(outDir, doc_set_id + str(doc_id))
        print(f_path + " " + doc_set_id + str(doc_id))
        new_files.append(new_file)
        with open(new_file, "w+") as f:
            f.write("")
        copyfile(full_path, new_file)
        doc_id += 1
        
    create_labels(filesList, os.path.join(outDir, "000.label"))
    remove_boundaries(new_files)
    
def run_incremental(originalRefPath, otherDocsDir):
    filesList = []
    for f_path in os.listdir(otherDocsDir):
        full_path = os.path.join(otherDocsDir, f_path)
        filesList.append(full_path)
    
    for i in range(1, len(filesList)+1):
        file_group = filesList[:i]
        group_dir = os.path.join(originalRefPath, "group_" + str(i))
        if os.path.exists(group_dir):
            shutil.rmtree(group_dir)
        os.mkdir(group_dir)
        for file_path in file_group:
            tmp_file = os.path.join(group_dir, ntpath.basename(file_path))
            with open(tmp_file, "w+") as f:
                f.write("")
            copyfile(file_path, tmp_file)
        run(originalRefPath, group_dir, "physics_L02_group" + str(i), "all")
        shutil.rmtree(group_dir)

'''
run("/home/pjdrm/Desktop/GoogleScraper/in_docs/physics", "/home/pjdrm/Desktop/GoogleScraper/docs_annoted/L02", "physics_L02_video", "video")
run("/home/pjdrm/Desktop/GoogleScraper/in_docs/physics", "/home/pjdrm/Desktop/GoogleScraper/docs_annoted/L02", "physics_L02_html", "html")
run("/home/pjdrm/Desktop/GoogleScraper/in_docs/physics", "/home/pjdrm/Desktop/GoogleScraper/docs_annoted/L02", "physics_L02_ppt", "ppt")
run("/home/pjdrm/Desktop/GoogleScraper/in_docs/physics", "/home/pjdrm/Desktop/GoogleScraper/docs_annoted/L02", "physics_L02_pdf", "pdf")
run_incremental("/home/pjdrm/Desktop/GoogleScraper/in_docs/physics", "/home/pjdrm/Desktop/GoogleScraper/docs_annoted/L02")
'''

run_type_pure("/home/pjdrm/Desktop/GoogleScraper/in_docs/physics", "/home/pjdrm/Desktop/GoogleScraper/docs_annoted/L02", "physics_L02_pure_ppt", "ppt")
        
