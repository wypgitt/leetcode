#
# @lc app=leetcode id=2023 lang=python3
#
# [2023] Number of Pairs of Strings With Concatenation Equal to Target
#
# https://leetcode.com/problems/number-of-pairs-of-strings-with-concatenation-equal-to-target/description/
#
# algorithms
# Medium (75.45%)
# Likes:    752
# Dislikes: 57
# Total Accepted:    65.8K
# Total Submissions: 87.2K
# Testcase Example:  "[\"777\",\"7\",\"77\",\"77\"]\n\"7777\""
#
# Given an array of digit strings nums and a digit string target, return the
# number of pairs of indices (i, j) (where i != j) such that the concatenation
# of nums[i] + nums[j] equals target.
#
#
#
# Example 1:
#
# Input: nums = ["777","7","77","77"], target = "7777"
# Output: 4
# Explanation: Valid pairs are:
# - (0, 1): "777" + "7"
# - (1, 0): "7" + "777"
# - (2, 3): "77" + "77"
# - (3, 2): "77" + "77"
#
# Example 2:
#
# Input: nums = ["123","4","12","34"], target = "1234"
# Output: 2
# Explanation: Valid pairs are:
# - (0, 1): "123" + "4"
# - (2, 3): "12" + "34"
#
# Example 3:
#
# Input: nums = ["1","1","1"], target = "11"
# Output: 6
# Explanation: Valid pairs are:
# - (0, 1): "1" + "1"
# - (1, 0): "1" + "1"
# - (0, 2): "1" + "1"
# - (2, 0): "1" + "1"
# - (1, 2): "1" + "1"
# - (2, 1): "1" + "1"
#
#
#
# Constraints:
#
#
# 2 <= nums.length <= 100
#
#
# 1 <= nums[i].length <= 100
#
#
# 2 <= target.length <= 100
#
#
# nums[i] and target consist of digits.
#
#
# nums[i] and target do not have leading zeros.
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def numOfPairs(self, nums: List[str], target: str) -> int:
        """
        Interview explanation:
        Count ordered pairs i != j with nums[i]+nums[j] == target.

        Algorithm:
        - For each distinct prefix a of target, add cnt[a]*cnt[suffix],
          adjusting when a == suffix.

        Complexity: O(n * L) time, O(n) space.
        """
        cnt = Counter(nums)
        ans = 0
        for a, c in cnt.items():
            if not target.startswith(a):
                continue
            b = target[len(a):]
            if a == b:
                ans += c * (c - 1)
            else:
                ans += c * cnt[b]
        return ans
# @lc code=end
