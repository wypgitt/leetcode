#
# @lc app=leetcode id=1794 lang=python3
#
# [1794] Count Pairs of Equal Substrings With Minimum Difference
#
# https://leetcode.com/problems/count-pairs-of-equal-substrings-with-minimum-difference/description/
#
# algorithms
# Medium (64.10%)
# Likes:    48
# Dislikes: 62
# Total Accepted:    2.5K
# Total Submissions: 4K
# Testcase Example:  "\"abcd\"\n\"bccda\""
#
#
# You are given two strings firstString and secondString that are
# 0-indexed and consist only of lowercase English letters. Count the
# number of index quadruples (i,j,a,b) that satisfy the following
# conditions:
#
# 0 <= i <= j < firstString.length
#
# 0 <= a <= b < secondString.length
#
# The substring of firstString that starts at the i^th character and ends
# at the j^th character (inclusive) is equal to the substring of
# secondString that starts at the a^th character and ends at the b^th
# character (inclusive).
#
# j - a is the minimum possible value among all quadruples that satisfy
# the previous conditions.
#
# Return the number of such quadruples.
#
# Example 1:
#
# Input: firstString = "abcd", secondString = "bccda"
# Output: 1
# Explanation: The quadruple (0,0,4,4) is the only one that satisfies all
# the conditions and minimizes j - a.
#
# Example 2:
#
# Input: firstString = "ab", secondString = "cd"
# Output: 0
# Explanation: There are no quadruples satisfying all the conditions.
#
# Constraints:
#
# 1 <= firstString.length, secondString.length <= 2 * 10^5
#
# Both strings consist only of lowercase English letters.
#
# @lc code=start
class Solution:
    def countQuadruplets(self, firstString: str, secondString: str) -> int:
        """
        Interview explanation:
        Premium: equal substrings reduce to the same character c used at its
        first index i in firstString and last index j in secondString. Among
        characters present in both strings, minimize (j − i); return how many
        characters achieve that minimum difference.

        Algorithm:
        - first[c] = first index in s1; last[c] = last index in s2.
        - For each c in both: d = last[c] - first[c]; track min d and its count.

        Complexity: O(n + m) time, O(Σ) space.
        """
        first = {}
        for i, ch in enumerate(firstString):
            if ch not in first:
                first[ch] = i
        last = {}
        for i, ch in enumerate(secondString):
            last[ch] = i
        best = float("inf")
        cnt = 0
        for ch, i in first.items():
            if ch in last:
                d = last[ch] - i
                if d < best:
                    best = d
                    cnt = 1
                elif d == best:
                    cnt += 1
        return cnt
# @lc code=end
