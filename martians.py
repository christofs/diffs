#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Filename: martians.py
# Author: Christof Schöch, 2016.

WorkDir = "/media/christof/data/Dropbox/0-Analysen/2016/martians/diffs4/"
InputTexts = WorkDir + "texts/*.txt"
DiffText = WorkDir + "martians_wdiffed.txt"
DiffTextPrep = WorkDir + "martians_wdiffed-prep.txt"
DiffTable = WorkDir + "DiffTable.csv"


import re
import pandas as pd
import Levenshtein as ld
import nltk
import glob
import os


def sentence_splitter(InputTexts): 
    """Splits a text into individual sentences. (Do before using wdiff.)"""
    for file in glob.glob(InputTexts): 
        filename = os.path.basename(file)[:-4]
        with open(file, "r") as inf: 
            text = inf.read()
            text = nltk.sent_tokenize(text)
            newtext = ""
            for sent in text: 
                newtext = newtext + sent + "\n"
            with open(WorkDir + filename + "-sent.txt", "w") as outf:
                outf.write(newtext)


"""
Now do, in [WorkDir]/texts: wdiff --avoid-wraps martian1-sent.txt martian2-sent.txt > martians_wdiffed.txt
"""


def prepare_text(DiffText, DiffTextPrep): 
    """Make sure all locations of a modification are marked coherently."""
    with open(DiffText, "r") as df: 
        diff_text = df.read()
        diff_text = re.sub("]\n{", "] {", diff_text)
        diff_text = re.sub("]{", "] {", diff_text)
        diff_text = re.split("\n", diff_text)
        newtext = ""
        for sent in diff_text:
            sent = re.sub("-] ([^{])", "-] {++} \\1", sent)
            sent = re.sub("-]$", "-] {++}", sent)
            sent = re.sub("(\w) ({)", "\\1 [--] \\2", sent)
            sent = re.sub("^{\+", "[--] {+", sent)
            newtext = newtext + sent + "\n"
        with open(DiffTextPrep, "w") as outf:
            outf.write(newtext)



def extract_diffs(DiffTextPrep, DiffTable): 
    """Extract each location of a modification and classify it in a number of types."""
    with open(DiffTextPrep, "r") as df: 
        diff_text = df.read()
        diff_text = re.split("\n", diff_text)
        all_diffs = []
        line_number = 0
        for line in diff_text:
            #print(sent)
            line_number +=1
            pairs = re.findall("\[-.*?\-\] {\+.*?\+}", line, re.DOTALL)
            item_number = 0
            for item in pairs: 
                item_number += 1
                item_id = '{:05d}'.format(line_number)+"-"+str(item_number)
                item = re.split("\] {", item)
                #print(item_id, item)
                type = ""
                category = ""
                item1 = item[0][2:-1]
                item2 = item[1][1:-2]
                insertion = 0
                deletion = 0
                capitalization = 0
                whitespace = 0
                italics = 0
                punctuation = 0
                hyphenation = 0
                numbers = 0
                abreviation = 0
                condensation = 0
                expansion = 0
                tbc = 0
                combination = 0
                copyedit = 0
                content = 0
                cat_tbc = 0
                # Complete deletion or insertion
                if len(item1) == 0:
                    category = "tbc"
                    cat_tbc = 1
                    type = "insertion"
                    insertion = 1
                elif len(item2) == 0:
                    category = "tbc"
                    cat_tbc = 1
                    type = "deletion"
                    deletion = 1
                # Simple cases: only one criterion applies
                elif item1.lower() == item2.lower(): 
                    type = "capitalization"
                    category = "copyedit"
                    capitalization = 1
                    copyedit = 1
                elif re.sub(" ","",item1) == re.sub(" ","",item2): 
                    type = "whitespace"
                    category = "copyedit"
                    copyedit = 1
                    whitespace = 1
                elif re.sub("\*","",item1) == re.sub("\*","",item2): 
                    type = "italics"
                    category = "copyedit"
                    copyedit = 1
                    italics = 1
                elif re.sub("[\",';:!?\.\(\)]","",item1) == re.sub("[\",';:!?\.\(\)]","",item2): 
                    type = "punctuation"
                    category = "copyedit"
                    copyedit = 1
                    punctuation = 1
                elif re.sub("\-","",item1) == re.sub(" ","",item2): 
                    type = "hyphenation"
                    category = "copyedit"
                    copyedit = 1
                    hyphenation = 1
                elif re.sub(" ","",item1) == re.sub("\-","",item2): 
                    type = "hyphenation"
                    category = "copyedit"
                    copyedit = 1
                    hyphenation = 1
                elif bool(re.search(r'\d', item1+item2)) == True:
                    type = "numbers"
                    category = "copyedit"
                    copyedit = 1
                    numbers = 1
                # Composite cases: two criteria apply
                elif re.sub(" ","",item1.lower()) == re.sub(" ","",item2.lower()):
                    type = "combination"
                    category = "copyedit"
                    copyedit = 1
                    capitalization = 1                
                    whitespace = 1
                    combination = 1
                elif re.sub("\*","",item1) == re.sub("\*","",item2): 
                    type = "combination"
                    category = "copyedit"
                    copyedit = 1
                    capitalization = 1                
                    italics = 1
                    combination = 1
                elif re.sub("[\",';:!?\.\(\)]","",item1.lower()) == re.sub("[\",';:!?\.\(\)]","",item2.lower()):
                    category = "copyedit"
                    copyedit = 1
                    type = "combination"
                    capitalization = 1                
                    punctuation = 1
                    combination = 1
                elif re.sub("\-","",item1.lower()) == re.sub(" ","",item2.lower()): 
                    category = "copyedit"
                    copyedit = 1
                    type = "combination"
                    capitalization = 1                
                    hyphenation = 1
                    combination = 1
                elif re.sub(" ","",item1.lower()) == re.sub("\-","",item2.lower()): 
                    category = "copyedit"
                    copyedit = 1
                    type = "combination"
                    capitalization = 1       
                    hyphenation = 1
                    combination = 1
                elif re.sub("[\",';:!?\.\(\) ]","",item1.lower()) == re.sub("[\",';:!?\.\(\) ]","",item2.lower()):
                    category = "copyedit"
                    copyedit = 1
                    type = "combination"
                    punctuation = 1       
                    whitespace = 1
                    combination = 1
                elif re.sub("[\",';:!?\.\(\)\-]","",item1.lower()) == re.sub("[\",';:!?\.\(\)\-]","",item2.lower()):
                    category = "copyedit"
                    copyedit = 1
                    type = "combination"
                    punctuation = 1
                    hyphenation = 1       
                    combination = 1
                elif re.sub("[\",';:!?\.\(\)\- ]","",item1.lower()) == re.sub("[\",';:!?\.\(\)\- ]","",item2.lower()):
                    category = "copyedit"
                    copyedit = 1
                    type = "combination"
                    punctuation = 1
                    hyphenation = 1       
                    whitespace = 1       
                    combination = 1
                # If none of the more specific cases apply:
                elif len(item1) > len(item2)+3:
                    category = "tbc"
                    cat_tbc = 1
                    type = "condensation"
                    condensation = 1
                elif len(item2) > len(item1)+3:
                    category = "tbc"
                    cat_tbc = 1
                    type = "expansion"
                    expansion = 1
                # All still unclassified cases:
                else: 
                    category = "tbc"
                    cat_tbc = 1
                    type = "tbc"
                    tbc = 1
                levenshtein = ld.distance(item1, item2)
                complete_item = [item_id, item1, item2, category, type, levenshtein, insertion, deletion, capitalization, whitespace, italics, punctuation, hyphenation, numbers, abreviation, condensation, expansion, tbc, combination, copyedit, content, cat_tbc]
                all_diffs.append(complete_item)
    diff_df = pd.DataFrame(all_diffs, columns=["item-id", "version1", "version2", "category", "type", "levenshtein", "insertion", "deletion", "capitalization", "whitespace", "italics", "punctuation", "hyphenation", "numbers", "abreviation", "condensation", "expansion", "tbc", "combination", "cat=copyedit", "cat=content", "cat=tbc"])
    #print(diff_df)
    with open(DiffTable, "w") as dt: 
        diff_df.to_csv(dt, index=False, sep="\t")


def main(InputTexts, DiffText, DiffTextPrep, DiffTable):
    #sentence_splitter(InputTexts)
    #prepare_text(DiffText, DiffTextPrep)
    extract_diffs(DiffTextPrep, DiffTable)

main(InputTexts, DiffText, DiffTextPrep, DiffTable)
