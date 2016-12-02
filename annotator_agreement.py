import os
import pandas as pd
import numpy as np
import segeval
import matplotlib.pyplot as plt
import json
plt.style.use('ggplot')

U_VAL = 2
C_VAL = 1
NO_ANNO_VAL = 0

def segeval_converter(annotation):
    segeval_format = []
    sent_count = 0
    for sent in annotation:
        if sent == 1:
            segeval_format.append(sent_count+1)
            sent_count = 0
        else:
            sent_count += 1
    segeval_format.append(sent_count)
    return segeval_format
    
def get_seg_anno_dic(anno_matrix, annotators_ids, doc_id):
    seg_dic = {}
    for i, a_id in enumerate(annotators_ids):
        segeval_anno_format = segeval_converter(anno_matrix[i])
        seg_dic[a_id] = segeval_anno_format
    return {doc_id: seg_dic}
                                                              
def segs_count(filePath):
    global U_VAL, C_VAL, NO_ANNO_VAL    
    annotation = []
    with open(filePath, encoding="utf8", errors='ignore') as f:
        lins = f.readlines()
        if not "==========" in lins[0]:
            lins = lins[1:]
        lins = lins[1:-1]
        for lin in lins:
            lin = lin.strip()
            if "==========" in lin:
                #case where the annotator was not certain. Will represent with value U_VAL
                if "U" in lin:
                    annotation[-1] = U_VAL
                else:
                    annotation[-1] = C_VAL
            else:
                annotation.append(NO_ANNO_VAL)
                
    return annotation

def init_seg_dic(doc_full_dir):
    doc = os.listdir(doc_full_dir)[0]
    seg_dic = {}
    with open(os.path.join(doc_full_dir, doc), encoding="utf8", errors='ignore') as f:
        lins = f.readlines()
        i = 0
        for lin in lins:
            lin = lin.strip()
            if "==========" in lin:
                continue
            else:
                seg_dic[i] = 0
                i += 1
    return seg_dic

def plot_annotations(annotations, fileName, annotators_id, outFile):
    df2 = pd.DataFrame(annotations, columns=annotators_id)
    ax = df2.plot.bar(stacked=True)
    plt.yticks(np.arange(0, len(annotators_id)+1, 1))
    plt.setp( ax.get_xticklabels(), visible=False)
    plt.xlabel('Sentences', fontsize=14)
    plt.ylabel('#Boundaries', fontsize=14)
    plt.savefig(outFile)

def get_anno_ids(anno_files):
    ids = []
    for f in anno_files:
        ids.append(f[:-4].split("_")[-1])
    return ids

def normalize_val(j, n_lins, annotations):
    global U_VAL, C_VAL, NO_ANNO_VAL
    c_un = 0
    c_ce = 0
    for i in range(n_lins):
        anno = annotations[i][j]
        if anno == U_VAL:
            c_un += 1
        if anno == C_VAL:
            c_ce += 1
    if c_un == 1 and c_ce == 0:
        return NO_ANNO_VAL
    else:
        return C_VAL

'''
Uncertainty in the annotation is normalized by removing
boundaries that a single annotator marked as uncertain.
The remaining cases (multiple uncertainties or mixes of
certain and uncertain with different annotators) are converted
to certainty. 
'''
def normalize_anno_certainty(annotations):
    global U_VAL, C_VAL, NO_ANNO_VAL
    n_lins = len(annotations)
    n_cols = len(annotations[0])
    for j in range(n_cols):
        norm_val = normalize_val(j, n_lins, annotations)
        for i in range(n_lins):
            anno = annotations[i][j]
            if anno == U_VAL:
                annotations[i][j] = norm_val
'''
Changes all uncertain annotations to certain
'''                
def preserve_anno_uncertainty(annotations):
    global U_VAL, C_VAL
    n_lins = len(annotations)
    n_cols = len(annotations[0])
    for j in range(n_cols):
        for i in range(n_lins):
            anno = annotations[i][j]
            if anno == U_VAL:
                annotations[i][j] = C_VAL
                
def gen_pk_agreement(annotations, anno_ids):
    n_annotators = len(anno_ids)
    matrix_str = "\t"
    for annotator in anno_ids:
        matrix_str += annotator + "\t"
    matrix_str += "\n"
    for i in range(n_annotators):
        matrix_str += anno_ids[i] + "\t"
        for j in range(n_annotators):
            matrix_str += str(round(segeval.pk(segeval_converter(annotations[j]), segeval_converter(annotations[i])), 2)) + "\t"
        matrix_str += "\n"
    return matrix_str

def avg_pk_matrix(pk_matrix_list, anno_ids):
    dim = len(anno_ids)
    vals_pk_matrix = []
    for i in range(dim):
        matrix_lin = []
        for j in range(dim):
            matrix_lin.append([])
        vals_pk_matrix.append(matrix_lin)
        
    for pk_matrix in pk_matrix_list:
        for i, lin in enumerate(pk_matrix.split("\n")[1:]):
            lin = lin.strip()
            for j, col in enumerate(lin.split("\t")[1:]):
                vals_pk_matrix[i][j].append(float(col))
                
    avg_str_pk_matrix = "\t"
    for anno in anno_ids:
        avg_str_pk_matrix += anno + "\t\t\t"
        
    avg_str_pk_matrix += "\n"
    for i, anno in enumerate(anno_ids):
        avg_str_pk_matrix += anno + "\t"
        for j, anno2 in enumerate(anno_ids):
            pk_avg = round(np.average(vals_pk_matrix[i][j]), 2)
            std = round(np.std(vals_pk_matrix[i][j]), 2)
            avg_str_pk_matrix +=  str(pk_avg) + "+-" + str(std) + "\t"
        avg_str_pk_matrix += "\n"
    return avg_str_pk_matrix
            
def process_annotations(anno_dir, resDir, norm_flag = True):
    str_agreement = ""
    all_b_pi = []
    all_s_k = []
    all_s_pi = []
    all_pk_matrix = []
    
    for doc_dir in os.listdir(anno_dir):
        print(doc_dir)
        doc_full_dir = os.path.join(anno_dir, doc_dir)
        if "results" in doc_full_dir:
            continue
        annotations = []
        anno_ids = get_anno_ids(os.listdir(doc_full_dir))
        for anno_file in os.listdir(doc_full_dir):
            annotations.append(segs_count(os.path.join(doc_full_dir, anno_file)))
        if norm_flag:
            normalize_anno_certainty(annotations)
        else:
            preserve_anno_uncertainty(annotations)
        pk_matrix = gen_pk_agreement(annotations, anno_ids)
        all_pk_matrix.append(pk_matrix)
        str_agreement += "\n" + doc_dir + "\nPk Agreement\n" + pk_matrix
        seg_ann_dic = {"items": {}, "segmentation_type": "linear"}
        seg_ann_dic["items"] = get_seg_anno_dic(annotations, anno_ids, doc_dir)
        with open('tmp_json.txt', 'w') as outfile:
            json.dump(seg_ann_dic, outfile)
        dataset = segeval.input_linear_mass_json('tmp_json.txt')
        b_pi = float(segeval.actual_agreement_linear(dataset))
        all_b_pi.append(b_pi)
        
        s_k = float(segeval.fleiss_kappa_linear(dataset))
        all_s_k.append(s_k)
        
        s_pi = float(segeval.fleiss_pi_linear(dataset))
        all_s_pi.append(s_pi)
        
        str_agreement += "\nS-pi* " + str(s_pi) + "\nS-K* " + str(s_k) + "\nB-pi* " + str(b_pi) + "\n"
        plot_annotations(np.array(annotations).T, doc_dir, anno_ids, os.path.join(resDir, doc_dir + "_results.png"))
    
    str_agreement += "\nAverage Agreement\n\nPk avg\n"
    str_agreement += avg_pk_matrix(all_pk_matrix, anno_ids) + "\n"
    str_agreement += "S-pi* avg: " + str(np.average(all_s_pi)) + " +- " + str(np.std(all_s_pi)) + "\n"
    str_agreement += "S-K* avg: " + str(np.average(all_s_k)) + " +- " + str(np.std(all_s_k)) + "\n"
    str_agreement += "B-pi* avg: " + str(np.average(all_b_pi)) + " +- " + str(np.std(all_b_pi))
    with open(os.path.join(resDir, "agreement.txt"), "w+") as f:
        f.write(str_agreement[1:])
        
    print("Done")
       
process_annotations("/home/pjdrm/workspace/TopicSegmentationScripts/human_annotations/test_annotations_hr_pm", "/home/pjdrm/workspace/TopicSegmentationScripts/human_annotations/test_annotations_hr_pm/results", False)
process_annotations("/home/pjdrm/workspace/TopicSegmentationScripts/human_annotations/test_annotations_hr_pm", "/home/pjdrm/workspace/TopicSegmentationScripts/human_annotations/test_annotations_hr_pm/results_normalized", True)
#print(segeval_converter([0, 0, 1, 1, 0, 0, 0, 0]))