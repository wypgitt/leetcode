#
# @lc app=leetcode id=1181 lang=python3
#
# [1181] Before and After Puzzle
#
# https://leetcode.com/problems/before-and-after-puzzle/description/
#
# algorithms
# Medium (51.85%)
# Likes:    93
# Dislikes: 158
# Total Accepted:    13.1K
# Total Submissions: 25.3K
# Testcase Example:  "[\"writing code\",\"code rocks\"]"
#
#
# Given a list of phrases, generate a list of Before and After puzzles.
#
# A phrase is a string that consists of lowercase English letters and
# spaces only. No space appears in the start or the end of a phrase. There
# are no consecutive spaces in a phrase.
#
# Before and After puzzles are phrases that are formed by merging two
# phrases where the last word of the first phrase is the same as the first
# word of the second phrase. Note that only the last word of the first
# phrase and the first word of the second phrase are merged in this
# process.
#
# Return the Before and After puzzles that can be formed by every two
# phrases phrases[i] and phrases[j] where i != j. Note that the order of
# matching two phrases matters, we want to consider both orders.
#
# You should return a list of distinct strings sorted lexicographically,
# after removing all duplicate phrases in the generated Before and After
# puzzles.
#
# Example 1:
#
# Input: phrases = ["writing code","code rocks"]
#
# Output: ["writing code rocks"]
#
# Example 2:
#
# Input: phrases = ["mission statement","a quick bite to eat","a chip off
# the old block","chocolate bar","mission impossible","a man on a
# mission","block party","eat my words","bar of soap"]
#
# Output: ["a chip off the old block party","a man on a mission
# impossible","a man on a mission statement","a quick bite to eat my
# words","chocolate bar of soap"]
#
# Example 3:
#
# Input: phrases = ["a","b","a"]
#
# Output: ["a"]
#
# Example 4:
#
# Input: phrases = ["ab ba","ba ab","ab ba"]
#
# Output: ["ab ba ab","ba ab ba"]
#
# Constraints:
#
# 1 <= phrases.length <= 100
#
# 1 <= phrases[i].length <= 100
#
# @lc code=start

from typing import List


class Solution:
    def beforeAndAfterPuzzles(self, phrases: List[str]) -> List[str]:
        """
        Interview explanation:
        Premium: merge phrase i with phrase j (i≠j) when the last word of i
        equals the first word of j; joined phrase drops the duplicated word.
        Return sorted unique merges.

        Algorithm:
        - Split each phrase into words; group indices by first/last word.
        - For each pair with last(i)==first(j), i!=j: merge and collect in a set.
        - Return sorted list.

        Complexity: O(n^2 * L) time worst case, O(n^2 * L) space for results.
        """
        words = [p.split() for p in phrases]
        n = len(words)
        result = set()
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                if words[i][-1] == words[j][0]:
                    merged = ' '.join(words[i] + words[j][1:])
                    result.add(merged)
        return sorted(result)
# @lc code=end
