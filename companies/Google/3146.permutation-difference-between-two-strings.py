#
# @lc app=leetcode id=3146 lang=python3
#
# [3146] Permutation Difference between Two Strings
#
# https://leetcode.com/problems/permutation-difference-between-two-strings/description/
#
# algorithms
# Easy (88.01%)
# Likes:    203
# Dislikes: 17
# Total Accepted:    116.9K
# Total Submissions: 132.8K
# Testcase Example:  "\"abc\"\n\"bac\""
#
#
# You are given two strings s and t such that every character occurs at
# most once in s and t is a permutation of s.
#
# The permutation difference between s and t is defined as the sum of the
# absolute difference between the index of the occurrence of each
# character in s and the index of the occurrence of the same character in
# t.
#
# Return the permutation difference between s and t.
#
# Example 1:
#
# Input: s = "abc", t = "bac"
#
# Output: 2
#
# Explanation:
#
# For s = "abc" and t = "bac", the permutation difference of s and t is
# equal to the sum of:
#
# The absolute difference between the index of the occurrence of "a" in s
# and the index of the occurrence of "a" in t.
#
# The absolute difference between the index of the occurrence of "b" in s
# and the index of the occurrence of "b" in t.
#
# The absolute difference between the index of the occurrence of "c" in s
# and the index of the occurrence of "c" in t.
#
# That is, the permutation difference between s and t is equal to |0 - 1|
# + |1 - 0| + |2 - 2| = 2.
#
# Example 2:
#
# Input: s = "abcde", t = "edbac"
#
# Output: 12
#
# Explanation: The permutation difference between s and t is equal to |0 -
# 3| + |1 - 2| + |2 - 4| + |3 - 1| + |4 - 0| = 12.
#
# Constraints:
#
# 1 <= s.length <= 26
#
# Each character occurs at most once in s.
#
# t is a permutation of s.
#
# s consists only of lowercase English letters.
#

# @lc code=start
class Solution:
    def findPermutationDifference(self, s: str, t: str) -> int:
        """
        Interview explanation:
        Sum |index_s(c) - index_t(c)| over each character (unique in both).

        Algorithm:
        - Map each char in s to its index; walk t and accumulate abs diffs.

        Complexity: O(n) time, O(n) space.
        """
        pos = {c: i for i, c in enumerate(s)}
        return sum(abs(pos[c] - i) for i, c in enumerate(t))

    def findPermutationDifference_array(self, s: str, t: str) -> int:
        """
        Interview explanation:
        Alternate: fixed 26-slot index array instead of a hash map.

        Algorithm:
        - Store s indices in a list of size 26; sum abs against t indices.

        Complexity: O(n) time, O(1) extra space.
        """
        pos = [-1] * 26
        for i, c in enumerate(s):
            pos[ord(c) - 97] = i
        return sum(abs(pos[ord(c) - 97] - i) for i, c in enumerate(t))
# @lc code=end
