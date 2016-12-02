import re
import os

def is_good_lin(lin):
    if len(lin) < 5:
        return False
    if no_letters(lin):
        return False
    return True

def no_letters(line):
    match = re.search('[a-zA-Z]', line)
    if match == None:
        return True
    return False

def pre_process_file(filePath):
    final_str = ""
    with open(filePath, encoding="utf8", errors='ignore') as f:
        lins = f.readlines()
        for lin in lins:
            if lin == "==========\n":
                final_str += "==========\n"
                continue
            
            if is_good_lin(lin):
                final_str += lin
        final_str += "=========="
        
    with open(filePath, "w+") as f:
        f.write(final_str)
        
def run(rootDirPath):
    for dir in os.listdir(rootDirPath):
        for fileName in os.listdir(os.path.join(rootDirPath, dir)):
            pre_process_file(os.path.join(rootDirPath, dir, fileName))
    
run("/home/pjdrm/Desktop/docs_annoted")