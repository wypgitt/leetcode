#
# @lc app=leetcode id=830 lang=python3
#
# [830] Positions of Large Groups
#
# https://leetcode.com/problems/positions-of-large-groups/description/
#
# algorithms
# Easy (54.2%)
# Likes:    932
# Dislikes: 127
# Total Accepted:    124K
# Total Submissions: 229K
# Testcase Example:  "\"abbxxxxzzy\""
#
# In a string s of lowercase letters, these letters form consecutive groups of
# the same character.
#
# For example, a string like s = "abbxxxxzyy" has the groups "a", "bb", "xxxx",
# "z", and "yy".
#
# A group is identified by an interval [start, end], where start and end denote
# the start and end indices (inclusive) of the group. In the above example,
# "xxxx" has the interval [3,6].
#
# A group is considered large if it has 3 or more characters.
#
# Return the intervals of every large group sorted in increasing order by start
# index.
#
# Example 1:
#
# Input: s = "abbxxxxzzy"
# Output: [[3,6]]
# Explanation: "xxxx" is the only large group with start index 3 and end index
# 6.
#
# Example 2:
#
# Input: s = "abc"
# Output: []
# Explanation: We have groups "a", "b", and "c", none of which are large
# groups.
#
# Example 3:
#
# Input: s = "abcdddeeeeaabbbcd"
# Output: [[3,5],[6,9],[12,14]]
# Explanation: The large groups are "ddd", "eeee", and "bbb".
#
# Constraints:
#
# 1 <= s.length <= 1000
#
# s contains lowercase English letters only.
#

# @lc code=start

from typing import List


class Solution:
    def largeGroupPositions(self, s: str) -> List[List[int]]:
        """
        Interview explanation:
        Scan for runs of identical letters; if run length ≥ 3, record [start, end].

        Algorithm:
        - Two pointers / single pass: when char changes, check previous run.

        Complexity: O(n) time, O(1) extra space.
        """
        n = len(s)
        res = []
        i = 0
        while i < n:
            j = i
            while j < n and s[j] == s[i]:
                j += 1
            if j - i >= 3:
                res.append([i, j - 1])
            i = j
        return res
# @lc code=end
