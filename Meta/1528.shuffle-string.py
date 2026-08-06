#
# @lc app=leetcode id=1528 lang=python3
#
# [1528] Shuffle String
#
# https://leetcode.com/problems/shuffle-string/description/
#
# algorithms
# Easy (85.47%)
# Likes:    2961
# Dislikes: 548
# Total Accepted:    512K
# Total Submissions: 599K
# Testcase Example:  "\"codeleet\""
#
# You are given a string s and an integer array indices of the same length. The
# string s will be shuffled such that the character at the i^th position moves
# to indices[i] in the shuffled string.
#
# Return the shuffled string.
#
# Example 1:
#
# Input: s = "codeleet", indices = [4,5,6,7,0,2,1,3]
# Output: "leetcode"
# Explanation: As shown, "codeleet" becomes "leetcode" after shuffling.
#
# Example 2:
#
# Input: s = "abc", indices = [0,1,2]
# Output: "abc"
# Explanation: After shuffling, each character remains in its position.
#
# Constraints:
#
# s.length == indices.length == n
#
# 1 <= n <= 100
#
# s consists of only lowercase English letters.
#
# 0 <= indices[i] < n
#
# All values of indices are unique.
#

# @lc code=start
from typing import List


class Solution:
    def restoreString(self, s: str, indices: List[int]) -> str:
        """
        Interview explanation:
        Shuffle: character s[i] moves to index indices[i]. Build result array.

        Algorithm:
        - res=['']*n; res[indices[i]]=s[i]; join.

        Complexity: O(n) time/space.
        """
        n = len(s)
        res = [""] * n
        for i, ch in enumerate(s):
            res[indices[i]] = ch
        return "".join(res)
# @lc code=end
