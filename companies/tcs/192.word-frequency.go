package leetcode

// SolutionShell192 is the shell answer for LeetCode 192. It splits words onto
// separate lines, sorts so equal words become adjacent, counts with uniq -c,
// sorts by descending frequency, and prints word then count.
const SolutionShell192 = `tr -s ' ' '\n' < words.txt | sort | uniq -c | sort -nr | awk '{print $2, $1}'`
