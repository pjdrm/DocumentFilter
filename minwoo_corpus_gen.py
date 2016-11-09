'''
Created on Aug 25, 2016

@author: Pedro Mota
'''
import os
from shutil import copyfile
import ntpath
import shutil
import re

config_template = "model.class = topicseg.segment.MultiSeg\n\ncorpus.datasetDir = data/$DATA_DIR\ncorpus.stopwordList = config/STOPWORD.list\ncorpus.tokenizerModel = config/EnglishTok.bin\ncorpus.useStemmer = true\ncorpus.removeStopword = true\ncorpus.useTokenizer = true\noutput.outputDir = results/$RESULTS_DIR\n\noutput.rawDataDir = data/$DATA_DIR\nexp.output = results/$RESULTS_DIR/ind_scores.txt\nexp.perDocEval = true\n\nprior.dcm.global = 0.1\nprior.dcm.local = 0.1\n\nprior.doc.0.globalType = 5\nprior.doc.0.localType = 0.1\nprior.doc.0.length = 1\nprior.doc.1.globalType = 10\nprior.doc.1.localType = 1\nprior.doc.1.length = 0\n\nsampler.globalMerge = false"

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
        
def make_individual_tests(docsAnnotatedDir, outDir, results_root_dir, configDir):
    os.makedirs(configDir)
    for i, f_path in enumerate(os.listdir(docsAnnotatedDir)):
        full_path = os.path.join(docsAnnotatedDir, f_path)
        dest_dir = os.path.join(outDir, "doc" + str(i))
        os.makedirs(dest_dir)
        os.makedirs(os.path.join(results_root_dir, "doc" + str(i)))
        dest_file = os.path.join(dest_dir, "000.0")
        copyfile(full_path, dest_file)
        create_labels([dest_file], os.path.join(dest_dir, "000.label"))
        remove_boundaries([dest_file])
        with open(os.path.join(dest_dir, "file_names.map"), "w+") as f:
            f.write("000.0 " + f_path)
        config_arg = os.path.join(configDir.split("/")[-1], "doc" + str(i))
        config_txt = gen_config_template(config_arg, config_arg)
        with open(os.path.join(configDir, configDir.split("/")[-1] + "_doc" + str(i) + ".cfg"), "w+") as f:
            f.write(config_txt)
            
def gen_config_template(data_dir, results_dir):
    return config_template.replace("$DATA_DIR", data_dir).replace("$RESULTS_DIR", results_dir)
            
def make_group_tests(docsAnnotatedDir, outDir, docType, resultsPath, configDir):
    files_l = []
    suffix = docType
    if suffix == "_v":
        suffix = "video"
    dest_dir = os.path.join(outDir, "docs_" + suffix)
    os.makedirs(dest_dir)
    os.makedirs(os.path.join(resultsPath, "docs_" + suffix))
    config_arg = os.path.join(configDir.split("/")[-1], "docs_" + suffix)
    config_txt = gen_config_template(config_arg, config_arg)
    with open(os.path.join(configDir, configDir.split("/")[-1] + "_docs_" + suffix + ".cfg"), "w+") as f:
        f.write(config_txt)
    i = 0
    file_name_map = ""
    for f_path in os.listdir(docsAnnotatedDir):
        if docType in f_path or docType == "all":
            full_path = os.path.join(docsAnnotatedDir, f_path)
            dest_file = os.path.join(dest_dir, "000." + str(i))
            copyfile(full_path, dest_file)
            files_l.append(dest_file)
            file_name_map += "000." + str(i) + " " + f_path + "\n"
            i += 1
    create_labels(files_l, os.path.join(dest_dir, "000.label"))
    remove_boundaries(files_l)
    with open(os.path.join(dest_dir, "file_names.map"), "w+") as f:
        f.write(file_name_map[:-1])
        
def gen_run_script(configTopDir):
    script_txt = "CLASSPATH=\".:bin:lib/colt.jar:lib/lingpipe-3.4.0.jar:lib/MinCutSeg.jar:lib/mtj.jar:lib/options.jar:lib/log4j-1.2.15.jar:lib/trove-3.0.0a3.jar:lib/jargs.jar:lib/jdom.jar:lib/junit.jar:lib/opennlp-tools-1.4.3.jar:lib/maxent-2.5.2.jar:lib/trove.jar:lib/commons-math-2.1.jar\"\n"
    for configDir in os.listdir(configTopDir):
        for configFile in os.listdir(os.path.join(configTopDir, configDir)):
            script_txt += "java -Xmx8g -ea -Dfile.encoding=utf8 -cp ${CLASSPATH} topicseg.Runner -c config/" + os.path.join(configDir, configFile) + "\n"
    with open("run_minwoo_exp.sh", "w+") as f:
        f.write(script_txt)
    
        
def run2(docsAnnotatedDir, outDir, results_root_dir, config_dir):
    if os.path.isdir(outDir):
        shutil.rmtree(outDir)
    os.makedirs(outDir)
        
    if os.path.isdir(results_root_dir):
        shutil.rmtree(results_root_dir)
    os.makedirs(results_root_dir)
        
    if os.path.isdir(config_dir):
        shutil.rmtree(config_dir)
    os.makedirs(config_dir)
        
    for dir in os.listdir(docsAnnotatedDir):
        dir_full_path = os.path.join(docsAnnotatedDir, dir)
        outDir_full_path = os.path.join(outDir, dir)
        results_full_path = os.path.join(results_root_dir, dir)
        config_full_path = os.path.join(config_dir, dir)
        make_individual_tests(dir_full_path, outDir_full_path, results_full_path, config_full_path)
        make_group_tests(dir_full_path, outDir_full_path, "html", results_full_path, config_full_path)
        make_group_tests(dir_full_path, outDir_full_path, "pdf", results_full_path, config_full_path)
        make_group_tests(dir_full_path, outDir_full_path, "ppt", results_full_path, config_full_path)
        make_group_tests(dir_full_path, outDir_full_path, "_v", results_full_path, config_full_path)
        make_group_tests(dir_full_path, outDir_full_path, "all", results_full_path, config_full_path)
    gen_run_script(config_dir)
    
def run3(docsAnnotatedDir, outDir, results_root_dir, config_dir):
    if os.path.isdir(outDir):
        shutil.rmtree(outDir)
    os.makedirs(outDir)
        
    if os.path.isdir(results_root_dir):
        shutil.rmtree(results_root_dir)
    os.makedirs(results_root_dir)
        
    if os.path.isdir(config_dir):
        shutil.rmtree(config_dir)
    os.makedirs(config_dir)
        
    for dir in os.listdir(docsAnnotatedDir):
        dir_full_path = os.path.join(docsAnnotatedDir, dir)
        outDir_full_path = os.path.join(outDir, dir)
        results_full_path = os.path.join(results_root_dir, dir)
        config_full_path = os.path.join(config_dir, dir)
        if not os.path.isdir(config_full_path):
            os.makedirs(config_full_path)
        make_group_tests(dir_full_path, outDir_full_path, "all", results_full_path, config_full_path)
    gen_run_script(config_dir)
'''
run("/home/pjdrm/Desktop/GoogleScraper/in_docs/physics", "/home/pjdrm/Desktop/GoogleScraper/docs_annoted/L02", "physics_L02_video", "video")
run("/home/pjdrm/Desktop/GoogleScraper/in_docs/physics", "/home/pjdrm/Desktop/GoogleScraper/docs_annoted/L02", "physics_L02_html", "html")
run("/home/pjdrm/Desktop/GoogleScraper/in_docs/physics", "/home/pjdrm/Desktop/GoogleScraper/docs_annoted/L02", "physics_L02_ppt", "ppt")
run("/home/pjdrm/Desktop/GoogleScraper/in_docs/physics", "/home/pjdrm/Desktop/GoogleScraper/docs_annoted/L02", "physics_L02_pdf", "pdf")
run_incremental("/home/pjdrm/Desktop/GoogleScraper/in_docs/physics", "/home/pjdrm/Desktop/GoogleScraper/docs_annoted/L02")
'''

#run_type_pure("/home/pjdrm/Desktop/GoogleScraper/in_docs/physics", "/home/pjdrm/Desktop/GoogleScraper/docs_annoted/L02", "physics_L02_pure_ppt", "ppt")
run2("/home/pjdrm/Dropbox/PhD/Physics_Lectures_Annotations/docs_annoted", "minwoo_corpora", "minwoo_results", "minwoo_config")
#run3("/home/pjdrm/workspace/TopicSegmentationScripts/mw_data2_jacob", "minwoo_news_corpora", "minwoo_news_results", "minwoo_news_config")
        
