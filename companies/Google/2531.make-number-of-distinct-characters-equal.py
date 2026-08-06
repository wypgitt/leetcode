#
# @lc app=leetcode id=2531 lang=python3
#
# [2531] Make Number of Distinct Characters Equal
#
# https://leetcode.com/problems/make-number-of-distinct-characters-equal/description/
#
# algorithms
# Medium (27.81%)
# Likes:    617
# Dislikes: 160
# Total Accepted:    24.9K
# Total Submissions: 89.5K
# Testcase Example:  "\"ac\"\n\"b\""
#
# You are given two 0-indexed strings word1 and word2.
#
# A move consists of choosing two indices i and j such that 0 <= i <
# word1.length and 0 <= j < word2.length and swapping word1[i] with word2[j].
#
# Return true if it is possible to get the number of distinct characters in
# word1 and word2 to be equal with exactly one move. Return false otherwise.
#
#
#
# Example 1:
#
# Input: word1 = "ac", word2 = "b"
# Output: false
# Explanation: Any pair of swaps would yield two distinct characters in the
# first string, and one in the second string.
#
# Example 2:
#
# Input: word1 = "abcc", word2 = "aab"
# Output: true
# Explanation: We swap index 2 of the first string with index 0 of the second
# string. The resulting strings are word1 = "abac" and word2 = "cab", which both
# have 3 distinct characters.
#
# Example 3:
#
# Input: word1 = "abcde", word2 = "fghij"
# Output: true
# Explanation: Both resulting strings will have 5 distinct characters,
# regardless of which indices we swap.
#
#
#
# Constraints:
#
#
# 1 <= word1.length, word2.length <= 10^5
#
#
# word1 and word2 consist of only lowercase English letters.
#

# @lc code=start
class Solution:
    def isItPossible(self, word1: str, word2: str) -> bool:
        """
        Interview explanation:
        Swap exactly one char from word1 with one from word2; check if the two
        strings can end with equal distinct-character counts.

        Algorithm:
        - Count frequencies (26 letters). Try every (c1 in word1, c2 in word2).
        - Simulate the swap on counts; compare number of positive frequencies.
        - If c1 == c2, distinct counts are unchanged.

        Complexity: O(n + 26^2) time, O(1) space.
        """
        cnt1 = [0] * 26
        cnt2 = [0] * 26
        for c in word1:
            cnt1[ord(c) - 97] += 1
        for c in word2:
            cnt2[ord(c) - 97] += 1

        def distinct(cnt: list[int]) -> int:
            return sum(v > 0 for v in cnt)

        for i in range(26):
            if cnt1[i] == 0:
                continue
            for j in range(26):
                if cnt2[j] == 0:
                    continue
                if i == j:
                    if distinct(cnt1) == distinct(cnt2):
                        return True
                    continue
                # remove i from word1, add j; remove j from word2, add i
                d1 = distinct(cnt1) - (cnt1[i] == 1) + (cnt1[j] == 0)
                d2 = distinct(cnt2) - (cnt2[j] == 1) + (cnt2[i] == 0)
                if d1 == d2:
                    return True
        return False

    def isItPossible_simulate(self, word1: str, word2: str) -> bool:
        """
        Interview explanation:
        Alternate: mutate frequency arrays for each candidate swap and restore.

        Algorithm:
        - For each pair (i, j) with positive counts, apply swap, compare
          distinct counts, then undo.

        Complexity: O(n + 26^3) time, O(1) space.
        """
        cnt1 = [0] * 26
        cnt2 = [0] * 26
        for c in word1:
            cnt1[ord(c) - 97] += 1
        for c in word2:
            cnt2[ord(c) - 97] += 1
        for i in range(26):
            for j in range(26):
                if cnt1[i] == 0 or cnt2[j] == 0:
                    continue
                cnt1[i] -= 1
                cnt2[j] -= 1
                cnt1[j] += 1
                cnt2[i] += 1
                if sum(v > 0 for v in cnt1) == sum(v > 0 for v in cnt2):
                    return True
                cnt1[i] += 1
                cnt2[j] += 1
                cnt1[j] -= 1
                cnt2[i] -= 1
        return False
# @lc code=end
