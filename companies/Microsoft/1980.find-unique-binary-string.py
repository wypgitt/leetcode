#
# @lc app=leetcode id=1980 lang=python3
#
# [1980] Find Unique Binary String
#
# https://leetcode.com/problems/find-unique-binary-string/description/
#
# algorithms
# Medium (81.22%)
# Likes:    2868
# Dislikes: 100
# Total Accepted:    420K
# Total Submissions: 517K
# Testcase Example:  "[\"01\",\"10\"]"
#
# Given an array of strings nums containing n unique binary strings each of
# length n, return a binary string of length n that does not appear in nums. If
# there are multiple answers, you may return any of them.
#
# Example 1:
#
# Input: nums = ["01","10"]
# Output: "11"
# Explanation: "11" does not appear in nums. "00" would also be correct.
#
# Example 2:
#
# Input: nums = ["00","01"]
# Output: "11"
# Explanation: "11" does not appear in nums. "10" would also be correct.
#
# Example 3:
#
# Input: nums = ["111","011","001"]
# Output: "101"
# Explanation: "101" does not appear in nums. "000", "010", "100", and "110"
# would also be correct.
#
# Constraints:
#
# n == nums.length
#
# 1 <= n <= 16
#
# nums[i].length == n
#
# nums[i] is either '0' or '1'.
#
# All the strings of nums are unique.
#

# @lc code=start
from typing import List


class Solution:
    def findDifferentBinaryString(self, nums: List[str]) -> str:
        """
        Interview explanation:
        n binary strings of length n; find one missing. Cantor's diagonal:
        flip the i-th bit of nums[i].

        Algorithm:
        - ans[i] = '1' if nums[i][i]=='0' else '0'.

        Complexity: O(n) time, O(n) space.
        """
        return "".join("1" if nums[i][i] == "0" else "0" for i in range(len(nums)))

    def findDifferentBinaryString_set(self, nums: List[str]) -> str:
        """
        Interview explanation:
        Alternate: put nums in a set; try integers 0..n as n-bit strings.

        Algorithm:
        - S=set(nums); for i in 0..n: format i in n bits; return first missing.

        Complexity: O(n^2) time, O(n) space.
        """
        n = len(nums)
        S = set(nums)
        for i in range(n + 1):
            cand = format(i, f"0{n}b")
            if cand not in S:
                return cand
        return ""
# @lc code=end

