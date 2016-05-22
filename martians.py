#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Filename: martians.py
# Author: Christof Schöch, 2016.

WorkDir = "/media/christof/data/Dropbox/0-Analysen/2016/martians/diffs5/"
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
                item1 = item[0][2:-1]
                item2 = item[1][1:-2]
                #print(item_id, item)
                mod_type = ""
                mod_cat = ""
                cat_copyedit = 0
                cat_tbc = 0
                insertion = 0
                deletion = 0
                capitalization = 0
                whitespace = 0
                punctuation = 0
                hyphenation = 0
                numbers = 0
                abreviation = 0
                condensation_minor = 0
                expansion_minor = 0
                condensation_major = 0
                expansion_major = 0
                combination = 0
                tbc = 0
                # Complete deletion or insertion
                if len(item1) == 0 and ld.distance(item1, item2) < 5.5:
                    mod_cat = "other"
                    cat_tbc = 1
                    mod_type = "insertion-minor"
                    insertion = 1
                elif len(item1) == 0 and ld.distance(item1, item2) > 5.5:
                    mod_cat = "other"
                    cat_tbc = 1
                    mod_type = "insertion-major"
                    insertion = 1
                elif len(item2) == 0 and ld.distance(item1, item2) < 5.5:
                    mod_cat = "other"
                    cat_tbc = 1
                    mod_type = "deletion-minor"
                    deletion = 1
                elif len(item2) == 0 and ld.distance(item1, item2) > 5.5:
                    mod_cat = "other"
                    cat_tbc = 1
                    mod_type = "deletion-major"
                    deletion = 1
                # Simple cases: only one criterion applies
                elif item1.lower() == item2.lower(): 
                    mod_type = "capitalization-only"
                    mod_cat = "copyedit"
                    capitalization = 1
                    cat_copyedit = 1
                elif re.sub(" ","",item1) == re.sub(" ","",item2): 
                    mod_type = "whitespace-only"
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    whitespace = 1
                elif re.sub("[\",';:!?\.\(\)]","",item1) == re.sub("[\",';:!?\.\(\)]","",item2): 
                    mod_type = "punctuation-only"
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    punctuation = 1
                elif re.sub("\-","",item1) == re.sub(" ","",item2): 
                    mod_type = "hyphenation-only"
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    hyphenation = 1
                elif re.sub(" ","",item1) == re.sub("\-","",item2): 
                    mod_type = "hyphenation-only"
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    hyphenation = 1
                elif re.sub("km","kilometer",item1) == re.sub("kilometers","kilometer",item2): 
                    mod_type = "abreviation-only"
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    abreviation = 1
                elif re.sub("%","percent",item1) == item2: 
                    mod_type = "abreviation-only"
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    abreviation = 1
                elif re.sub("cm","centimeter",item1) == re.sub("centimeters","centimeter",item2): 
                    mod_type = "abreviation-only"
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    abreviation = 1
                elif re.sub("m","meter",item1) == re.sub("meters","meter",item2): 
                    mod_type = "abreviation-only"
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    abreviation = 1
                elif re.sub("L","liter",item1) == re.sub("liters","liter",item2): 
                    mod_type = "abreviation-only"
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    abreviation = 1
                elif re.sub("W","watts",item1) == item2: 
                    mod_type = "abreviation-only"
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    abreviation = 1
                elif re.sub("kg","kilogram",item1) == re.sub("kilograms","kilogram",item2): 
                    mod_type = "abreviation-only"
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    abreviation = 1
                elif re.sub("ml","mililiters",item1) == item2: 
                    mod_type = "abreviation-only"
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    abreviation = 1
                elif re.sub("kwh","kilowatt-hour",item1) == re.sub("kilowatt-hours","kilowatt-hour",item2): 
                    mod_type = "abreviation-only"
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    abreviation = 1
                elif re.sub("m/s","meters per second",item1) == re.sub("meters per second","meter per second",item2): 
                    mod_type = "abreviation-only"
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    abreviation = 1
                elif re.sub("Wh","watt hours",item1) == re.sub("watt hours","watt hour",item2): 
                    mod_type = "abreviation-only"
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    abreviation = 1
                elif re.sub("rps","revolutions per second",item1) == item2: 
                    mod_type = "abreviation-only"
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    abreviation = 1
                elif re.sub("Doctor","Dr.",item1) == item2: 
                    mod_type = "abreviation-only"
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    abreviation = 1
                elif re.sub("Ok","Okay",item1) == item2: 
                    mod_type = "abreviation-only"
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    abreviation = 1
                elif bool(re.search(r'\d', item1+item2)) == True: 
                    mod_type = "numbers-involved"
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    numbers = 1
                # Composite cases: two criteria apply
                elif re.sub("%","percent,",item1) == item2: 
                    mod_type = "combination"
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    abreviation = 1
                    punctuation = 1
                elif re.sub("ok","okay",item1.lower()) == item2.lower(): 
                    mod_type = "combination"
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    abreviation = 1
                    capitalization = 1
                elif re.sub(" ","",item1.lower()) == re.sub(" ","",item2.lower()):
                    mod_type = "combination"
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    capitalization = 1                
                    whitespace = 1
                    combination = 1
                elif re.sub("\*","",item1) == re.sub("\*","",item2): 
                    mod_type = "combination"
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    capitalization = 1                
                    italics = 1
                    combination = 1
                elif re.sub("[\",';:!?\.\(\)]","",item1.lower()) == re.sub("[\",';:!?\.\(\)]","",item2.lower()):
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    mod_type = "combination"
                    capitalization = 1                
                    punctuation = 1
                    combination = 1
                elif re.sub("\-","",item1.lower()) == re.sub(" ","",item2.lower()): 
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    mod_type = "combination"
                    capitalization = 1                
                    hyphenation = 1
                    combination = 1
                elif re.sub(" ","",item1.lower()) == re.sub("\-","",item2.lower()): 
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    mod_type = "combination"
                    capitalization = 1       
                    hyphenation = 1
                    combination = 1
                elif re.sub("[\",';:!?\.\(\) ]","",item1.lower()) == re.sub("[\",';:!?\.\(\) ]","",item2.lower()):
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    mod_type = "combination"
                    punctuation = 1       
                    whitespace = 1
                    combination = 1
                elif re.sub("[\",';:!?\.\(\)\-]","",item1.lower()) == re.sub("[\",';:!?\.\(\)\-]","",item2.lower()):
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    mod_type = "combination"
                    punctuation = 1
                    hyphenation = 1       
                    combination = 1
                elif re.sub("[\",';:!?\.\(\)\- ]","",item1.lower()) == re.sub("[\",';:!?\.\(\)\- ]","",item2.lower()):
                    mod_cat = "copyedit"
                    cat_copyedit = 1
                    mod_type = "combination"
                    punctuation = 1
                    hyphenation = 1       
                    whitespace = 1       
                    combination = 1
                # If none of the more specific cases apply:
                elif len(item1) > len(item2) and ld.distance(item1, item2) < 5.5:
                    mod_cat = "other"
                    cat_tbc = 1
                    mod_type = "condensation-minor"
                    condensation_minor = 1
                elif len(item1) > len(item2) and ld.distance(item1, item2) > 5.5:
                    mod_cat = "other"
                    cat_tbc = 1
                    mod_type = "condensation-major"
                    condensation_major = 1
                elif len(item1) != 0 and len(item2) > len(item1) and ld.distance(item1, item2) < 5.5:
                    mod_cat = "other"
                    cat_tbc = 1
                    mod_type = "expansion-minor"
                    expansion_minor = 1
                elif len(item1) != 0 and len(item2) > len(item1) and ld.distance(item1, item2) > 5.5:
                    mod_cat = "other"
                    cat_tbc = 1
                    mod_type = "expansion-major"
                    expansion_major = 1
                # All still unclassified cases:
                else: 
                    mod_cat = "other"
                    cat_tbc = 1
                    mod_type = "tbc"
                    tbc = 1
                levenshtein = ld.distance(item1, item2)
                char_delta = len(item1)-len(item2)
                char_delta_abs = abs(char_delta)
                complete_item = [item_id, item1, item2, mod_cat, mod_type, levenshtein, char_delta, char_delta_abs, capitalization, whitespace, punctuation, hyphenation, numbers, abreviation, condensation_major, condensation_minor, expansion_major, expansion_minor, insertion, deletion, combination, cat_copyedit, cat_tbc, tbc]
                all_diffs.append(complete_item)
    diff_df = pd.DataFrame(all_diffs, columns=["item-id", "version1", "version2", "category", "type", "levenshtein", "char-delta", "char-delta-abs", "capitalization", "whitespace", "punctuation", "hyphenation", "numbers", "abreviation", "cond-major", "cond-minor", "exp-major", "exp-minor", "insertion", "deletion", "combination", "cat=copyedit", "cat=tbc", "type-tbc"])
    #print(diff_df)
    with open(DiffTable, "w") as dt: 
        diff_df.to_csv(dt, index=False, sep="\t")


def main(InputTexts, DiffText, DiffTextPrep, DiffTable):
    #sentence_splitter(InputTexts)
    #prepare_text(DiffText, DiffTextPrep)
    extract_diffs(DiffTextPrep, DiffTable)

main(InputTexts, DiffText, DiffTextPrep, DiffTable)
