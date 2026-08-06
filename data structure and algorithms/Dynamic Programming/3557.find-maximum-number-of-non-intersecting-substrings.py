#
# @lc app=leetcode id=3557 lang=python3
#
# [3557] Find Maximum Number of Non Intersecting Substrings
#
# https://leetcode.com/problems/find-maximum-number-of-non-intersecting-substrings/description/
#
# algorithms
# Medium (31.18%)
# Likes:    86
# Dislikes: 3
# Total Accepted:    17.1K
# Total Submissions: 54.7K
# Testcase Example:  "\"abcdeafdef\""
#
#
# You are given a string word.
#
# Return the maximum number of non-intersecting substrings of word that
# are at least four characters long and start and end with the same
# letter.
#
# Example 1:
#
# Input: word = "abcdeafdef"
#
# Output: 2
#
# Explanation:
#
# The two substrings are "abcdea" and "fdef".
#
# Example 2:
#
# Input: word = "bcdaaaab"
#
# Output: 1
#
# Explanation:
#
# The only substring is "aaaa". Note that we cannot also choose "bcdaaaab"
# since it intersects with the other substring.
#
# Constraints:
#
# 1 <= word.length <= 2 * 10^5
#
# word consists only of lowercase English letters.
#

# @lc code=start
class Solution:
    def maxSubstrings(self, word: str) -> int:
        """
        Interview explanation:
        Want max non-overlapping substrings of length ≥ 4 that start and end
        with the same letter. Greedy earliest-finish is optimal for interval
        packing.

        Algorithm:
        - Track first index of each letter since the last taken substring.
        - When index i closes a letter first seen at f with i - f + 1 ≥ 4,
          take it, reset trackers, continue.
        - Taking the earliest possible end leaves maximal room for later picks.

        Complexity: O(n) time, O(1) space.
        """
        first = [-1] * 26
        ans = 0
        for i, ch in enumerate(word):
            idx = ord(ch) - 97
            if first[idx] == -1:
                first[idx] = i
            elif i - first[idx] + 1 >= 4:
                ans += 1
                first = [-1] * 26
        return ans
# @lc code=end
