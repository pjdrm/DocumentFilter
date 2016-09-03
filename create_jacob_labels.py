'''
Created on Aug 30, 2016

@author: root
'''
import os
from shutil import copyfile
import ntpath
import shutil

def run_pure_types_jacob(outDir, doc_annotated_dir, ref_file_path):
    if os.path.exists(outDir):
        shutil.rmtree(outDir)
        
    test_dirs = ["pure_video", "pure_html", "pure_pdf", "pure_ppt"]
    os.mkdir(outDir)
    os.mkdir(os.path.join(outDir, "pure_video"))
    os.mkdir(os.path.join(outDir, "pure_html"))
    os.mkdir(os.path.join(outDir, "pure_pdf"))
    os.mkdir(os.path.join(outDir, "pure_ppt"))
    for t_dir in test_dirs:
        os.mkdir(os.path.join(outDir, t_dir, "enhanchers"))
        os.mkdir(os.path.join(outDir, t_dir, "tests"))
        
    type_dic = {}
    type_dic["pure_video"] = [ref_file_path]
    type_dic["pure_html"] = []
    type_dic["pure_pdf"] = []
    type_dic["pure_ppt"] = []
    docs_txt_dir = doc_annotated_dir.replace("annoted", "txt")
    for doc_name in os.listdir(doc_annotated_dir):
        if "_v" in doc_name or doc_name.endswith(".ref"):
            type_dic["pure_video"].append(os.path.join(doc_annotated_dir, doc_name))
        else:
            with open(os.path.join(docs_txt_dir, doc_name.replace("_processed_annotated", "")[4:])) as f:
                f.readline()
                type = f.readline()[1:-1]
                type_dic["pure_"+type].append(os.path.join(doc_annotated_dir, doc_name))
                
    for type in type_dic:
        for doc_path in type_dic[type]:
            dest_file = os.path.join(outDir, type, "enhanchers", ntpath.basename(doc_path).replace(".txt", ".ref"))
            with open(dest_file, "w+", encoding="utf8", errors="ignore") as f:
                f.write("")
                copyfile(doc_path, dest_file)
                
            dest_file = os.path.join(outDir, type, "tests", ntpath.basename(doc_path).replace(".txt", ".ref"))
            with open(dest_file, "w+", encoding="utf8", errors="ignore") as f:
                f.write("")
                copyfile(doc_path, dest_file)
        
    
    
def run_incremental(originalRefPath, otherDocsDir):
    filesList = []
    for f_path in os.listdir(otherDocsDir):
        full_path = os.path.join(otherDocsDir, f_path)
        filesList.append(full_path)
    
    for i in range(1, len(filesList)+1):
        file_group = filesList[:i]
        group_dir = "group_jacob_" + str(i) + "_" + ntpath.basename(originalRefPath).split("_")[0][:-4]
        if os.path.exists(group_dir):
            shutil.rmtree(group_dir)
        os.mkdir(group_dir)
        os.mkdir(group_dir + "/enhanchers")
        group_dir += "/enhanchers"
        for file_path in file_group:
            tmp_file = os.path.join(group_dir, ntpath.basename(file_path))
            with open(tmp_file, "w+", encoding="utf8", errors="ignore") as f:
                f.write("")
                copyfile(file_path, tmp_file)
                str_tmp = f.read()
            with open(tmp_file, "w+", encoding="utf8", errors="ignore") as f:
                str_tmp = str_tmp.replace("==========\n", "").replace("==========", "")
                f.write(str_tmp)
                
        test_dir = "group_jacob_" + str(i) + "_" + ntpath.basename(originalRefPath).split("_")[0][:-4] + "/tests"
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        os.mkdir(test_dir)
        
        test_file = os.path.join(test_dir, ntpath.basename(originalRefPath))
        with open(test_file, "w+", encoding="utf8", errors="ignore") as f:
                f.write("")
        copyfile(originalRefPath, test_file)

run_incremental("/home/pjdrm/Desktop/GoogleScraper/in_docs/physics/L02.ref", "/home/pjdrm/Desktop/GoogleScraper/docs_annoted/L02")
#run_pure_types_jacob("physics_L02_pure_types_jacob", "/home/pjdrm/Desktop/GoogleScraper/docs_annoted/L02", "/home/pjdrm/Desktop/GoogleScraper/in_docs/physics/L02.ref")