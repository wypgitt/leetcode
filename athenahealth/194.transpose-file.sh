#!/usr/bin/env bash
# LeetCode 194 — Transpose File (submit this in the Shell tab).
# Reads space-separated columns from file.txt; prints transposed rows to stdout.

awk '
{
    for (i = 1; i <= NF; i++) {
        line[i] = (NR > 1 ? line[i] " " : "") $i
    }
}
END {
    for (i = 1; i <= NF; i++) {
        print line[i]
    }
}' file.txt
