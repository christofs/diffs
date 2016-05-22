#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Filename: split_narration.py
# Authors: #cf
# 2016-05-21



# TODO: We need to know how many lines (not: edits) are first / third person narration!



import re
import os
import glob
import pandas as pd


WorkDir = "/media/christof/data/Dropbox/0-Analysen/2016/martians/narration/"
DiffTable = WorkDir+"DiffTable_narration.csv"
TextFirst = WorkDir+"DiffedFirst.txt"
TextThird = WorkDir+"DiffedThird.txt"


def split_narration(DiffTable, TextFirst, TextThird): 
    """
    Distinguish edits by their context regarding narrative perspective; visualize.
    """
    print("get_lines...")
    
    # Open and read the two text parts
    with open(TextFirst, "r") as FirstFile: 
        TextFirst = FirstFile.read()
    with open(TextThird, "r") as ThirdFile: 
        TextThird = ThirdFile.read()

        print("\n== Basic data ==")
        TextFirstLines = re.split("\n", TextFirst)
        TextThirdLines = re.split("\n", TextThird)
        print("Length of text in lines: First", len(TextFirstLines), "; Third", len(TextThirdLines))
        TextFirstTokens = re.split("\W", TextFirst)
        TextThirdTokens = re.split("\W", TextThird)
        print("Length of text in tokens: First", len(TextFirstTokens), "; Third", len(TextThirdTokens))
        AvgLineLengthFirst = len(TextFirstTokens) / len(TextFirstLines)
        AvgLineLengthThird = len(TextThirdTokens) / len(TextThirdLines)
        print("Average length of lines (in tokens): First", str(AvgLineLengthFirst), "; Third", str(AvgLineLengthThird))
        

    # Open and read the DiffTable
    with open(DiffTable, "r") as InFile:
        Diffs = pd.DataFrame.from_csv(InFile, sep="\t")
        #print(Diffs.head())
        GroupedDiffs = Diffs.groupby("narration")
        GD = GroupedDiffs
        #print(GroupedDiffs.head())
        #print(len(GroupedDiffs))

        # The sums of various data about first and third together 
        EditsBoth = GD.sum()
        #print(EditsBoth)
        
        # The sums of various data separated into first and third
        EditsFirst = GD.get_group("first")
        EditsThird = GD.get_group("third")
        
        # How many edits where there?
        EditsFirstCount = len(EditsFirst)
        EditsThirdCount = len(EditsThird)
        print("Number of edits (absolute sum): First", EditsFirstCount, "; Third", EditsThirdCount)

        # What was the cumulated levenshtein difference? Absolute difference of characters?
        LevenshteinFirst = EditsBoth.loc["first","levenshtein"]
        LevenshteinThird = EditsBoth.loc["third","levenshtein"]
        print("Levenshtein distances (absolute sum): First", LevenshteinFirst, "; Third", LevenshteinThird)
        CharDeltaAbsFirst = EditsBoth.loc["first","char-delta-abs"]
        CharDeltaAbsThird = EditsBoth.loc["third","char-delta-abs"]
        print("Absolute Char Delta (absolute sum): First", CharDeltaAbsFirst, "; Third", CharDeltaAbsThird)

        print("\n== Relative counts first vs. third ==")
        # What was the relative number of edits (per line of text)?
        EditsFirstCountRel = len(EditsFirst) / len(TextFirstLines)
        EditsThirdCountRel = len(EditsThird) / len(TextThirdLines)
        print("Number of edits (relative to lines): First", EditsFirstCountRel, "; Third", EditsThirdCountRel)

        # What was the relative number of edits (per token of text)?
        EditsFirstCountRel = len(EditsFirst) / len(TextFirstTokens)
        EditsThirdCountRel = len(EditsThird) / len(TextThirdTokens)
        print("Number of edits (relative to tokens): First", EditsFirstCountRel, "; Third", EditsThirdCountRel)


        # What was the relative levenshtein difference and absolute difference of characters relative to the number of edits?
        LevenshteinRelFirst = LevenshteinFirst / EditsFirstCount
        LevenshteinRelThird = LevenshteinThird / EditsThirdCount
        print("Levenshtein distance (relative to edits): First", LevenshteinRelFirst, "; Third", LevenshteinRelThird)
        CharDeltaAbsRelFirst = CharDeltaAbsFirst / EditsFirstCount
        CharDeltaAbsRelThird = CharDeltaAbsThird / EditsThirdCount
        print("Absolute Char Delta (relative to edits): First", CharDeltaAbsRelFirst, "; Third", CharDeltaAbsRelThird)
        
        # What was the relative levenshtein difference and absolute difference of characters relative to the number of lines?
        LevenshteinRelFirst = LevenshteinFirst / len(TextFirstLines)
        LevenshteinRelThird = LevenshteinThird / len(TextThirdLines)
        print("Levenshtein distance (relative to lines): First", LevenshteinRelFirst, "; Third", LevenshteinRelThird)
        CharDeltaAbsRelFirst = CharDeltaAbsFirst / len(TextFirstLines)
        CharDeltaAbsRelThird = LevenshteinThird / len(TextFirstLines)
        print("Absolute Char Delta (relative to lines): First", CharDeltaAbsRelFirst, "; Third", CharDeltaAbsRelThird)
                
        # What was the relative levenshtein difference and absolute difference of characters relative to the number of tokens?
        LevenshteinRelFirst = LevenshteinFirst / len(TextFirstTokens)
        LevenshteinRelThird = LevenshteinThird / len(TextThirdTokens)
        print("Levenshtein distance (relative to tokens): First", LevenshteinRelFirst, "; Third", LevenshteinRelThird)
        CharDeltaAbsRelFirst = CharDeltaAbsFirst / len(TextFirstTokens)
        CharDeltaAbsRelThird = CharDeltaAbsThird / len(TextThirdTokens)
        print("Absolute Char Delta (relative to tokens): First", CharDeltaAbsRelFirst, "; Third", CharDeltaAbsRelThird)

        print("\n== Data on doubly grouped data: first/third and copyedit/significant edits ==")        
        DoubleGroupedDiffs = Diffs.groupby(["narration","category"])
        DGD = DoubleGroupedDiffs

        FirstCopy = DGD.get_group(("first","copyedit"))
        ThirdCopy = DGD.get_group(("third","copyedit"))
        FirstSign = DGD.get_group(("first","other"))
        ThirdSign = DGD.get_group(("third","other"))
        print("Number of edits: First copyedits", len(FirstCopy), "; First significant", len(FirstSign))
        print("Number of edits: Third copyedits", len(ThirdCopy), "; Third significant", len(ThirdSign))
        print("Proportion of significant edits: First", len(FirstSign)/len(EditsFirst), "; Third", len(ThirdSign)/len(EditsThird))
        print("Proportion of copyedits: First", len(FirstCopy)/len(EditsFirst), "; Third", len(ThirdCopy)/len(EditsThird))
               

    print("\nDone.")
    

split_narration(DiffTable, TextFirst, TextThird)
    

