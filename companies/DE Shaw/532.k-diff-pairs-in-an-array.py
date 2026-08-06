#
# @lc app=leetcode id=532 lang=python3
#
# [532] K-diff Pairs in an Array
#
# https://leetcode.com/problems/k-diff-pairs-in-an-array/description/
#
# algorithms
# Medium (46.2%)
# Likes:    4193
# Dislikes: 2294
# Total Accepted:    440K
# Total Submissions: 953K
# Testcase Example:  "[3,1,4,1,5]"
#
# Given an array of integers nums and an integer k, return the number of unique
# k-diff pairs in the array.
#
# A k-diff pair is an integer pair (nums[i], nums[j]), where the following are
# true:
#
# 0 <= i, j < nums.length
#
# i != j
#
# |nums[i] - nums[j]| == k
#
# Notice that |val| denotes the absolute value of val.
#
# Example 1:
#
# Input: nums = [3,1,4,1,5], k = 2
# Output: 2
# Explanation: There are two 2-diff pairs in the array, (1, 3) and (3, 5).
# Although we have two 1s in the input, we should only return the number of
# unique pairs.
#
# Example 2:
#
# Input: nums = [1,2,3,4,5], k = 1
# Output: 4
# Explanation: There are four 1-diff pairs in the array, (1, 2), (2, 3), (3, 4)
# and (4, 5).
#
# Example 3:
#
# Input: nums = [1,3,1,5,4], k = 0
# Output: 1
# Explanation: There is one 0-diff pair in the array, (1, 1).
#
# Constraints:
#
# 1 <= nums.length <= 10^4
#
# -10^7 <= nums[i] <= 10^7
#
# 0 <= k <= 10^7
#

# @lc code=start
from collections import Counter
from typing import List
class Solution:
    def findPairs(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Count unique pairs (i, j) with i != j and |nums[i]-nums[j]| == k.
        Use a frequency map: for k == 0 count values with freq >= 2; otherwise
        for each unique x check if x+k exists.

        Algorithm:
        - Counter(nums); iterate unique keys with the rules above.

        Complexity: O(n) time, O(n) space.
        """
        if k < 0:
            return 0
        freq = Counter(nums)
        if k == 0:
            return sum(1 for v in freq.values() if v >= 2)
        return sum(1 for x in freq if x + k in freq)
# @lc code=end

