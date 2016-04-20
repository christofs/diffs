#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Filename: martians.py
# Author: Christof Schöch, 2016.

WorkDir = "/home/christof/Dropbox/0-Analysen/2016/martians/diffs2/"
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
Now do: wdiff --avoid-wraps martians1-sent.txt martians2-sent.txt > martians_wdiffed.txt
"""


def prepare_text(DiffText, DiffTextPrep): 
    """Make sure all locations of a modification are marked coherently."""
    with open(DiffText, "r") as df: 
        filename = os.path.basename(DiffText)[:-4]
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
        sent_number = 0
        for sent in diff_text:
            #print(sent)
            sent_number +=1
            pairs = re.findall("\[-.*?\-\] {\+.*?\+}", sent, re.DOTALL)
            item_number = 0
            for item in pairs: 
                item_number += 1
                item_id = str(sent_number)+"-"+str(item_number)
                item = re.split("\] {", item)
                #print(item_id, item)
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
                condensation = 0
                expansion = 0
                tbc = 0
                if len(item1) == 0:
                    type = "insertion"
                    insertion = 1
                elif len(item2) == 0:
                    type = "deletion"
                    deletion = 1
                elif item1.lower() == item2.lower(): 
                    type = "capitalization"
                    capitalization = 1
                elif re.sub(" ","",item1) == re.sub(" ","",item2): 
                    type = "whitespace"
                    whitespace = 1
                elif re.sub("\*","",item1) == re.sub("\*","",item2): 
                    type = "italics"
                    italics = 1
                elif re.sub("[\",';:!?\.\(\)]","",item1) == re.sub("[\",';:!?\.\(\)]","",item2): 
                    type = "punctuation"
                    punctuation = 1
                elif re.sub("\-","",item1) == re.sub(" ","",item2): 
                    type = "hyphenation"
                    hyphenation = 1
                elif re.sub(" ","",item1) == re.sub("\-","",item2): 
                    type = "hyphenation"
                    hyphenation = 1
                elif bool(re.search(r'\d', item1+item2)) == True:
                    type = "numbers"
                    numbers = 1
                elif len(item1) > len(item2)+3:
                    type = "condensation"
                    condensation = 1
                elif len(item2) > len(item1)+3:
                    type = "expansion"
                    expansion = 1
                else: 
                    type = "tbc"
                    tbc = 1
                levenshtein = ld.distance(item1, item2)
                complete_item = [item_id, item1, item2, levenshtein, type, insertion, deletion, capitalization, whitespace, italics, punctuation, hyphenation, numbers, condensation, expansion, tbc]
                all_diffs.append(complete_item)
    diff_df = pd.DataFrame(all_diffs, columns=["item-id","version1","version2", "levenshtein",  "type", "insertion", "deletion", "capitalization", "whitespace", "italics", "punctuation", "hyphenation", "numbers", "condensation", "expansion", "tbc"])
    #print(diff_df)
    with open(DiffTable, "w") as dt: 
        diff_df.to_csv(dt, index=False)


def main(InputTexts, DiffText, DiffTextPrep, DiffTable):
    #sentence_splitter(InputTexts)
    #prepare_text(DiffText, DiffTextPrep)
    extract_diffs(DiffTextPrep, DiffTable)

main(InputTexts, DiffText, DiffTextPrep, DiffTable)
