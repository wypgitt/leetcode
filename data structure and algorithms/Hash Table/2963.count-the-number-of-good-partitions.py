#
# @lc app=leetcode id=2963 lang=python3
#
# [2963] Count the Number of Good Partitions
#
# https://leetcode.com/problems/count-the-number-of-good-partitions/description/
#
# algorithms
# Hard (50.23%)
# Likes:    328
# Dislikes: 5
# Total Accepted:    16.9K
# Total Submissions: 33.7K
# Testcase Example:  "[1,2,3,4]"
#
#
# You are given a 0-indexed array nums consisting of positive integers.
#
# A partition of an array into one or more contiguous subarrays is called
# good if no two subarrays contain the same number.
#
# Return the total number of good partitions of nums.
#
# Since the answer may be large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: nums = [1,2,3,4]
# Output: 8
# Explanation: The 8 possible good partitions are: ([1], [2], [3], [4]),
# ([1], [2], [3,4]), ([1], [2,3], [4]), ([1], [2,3,4]), ([1,2], [3], [4]),
# ([1,2], [3,4]), ([1,2,3], [4]), and ([1,2,3,4]).
#
# Example 2:
#
# Input: nums = [1,1,1,1]
# Output: 1
# Explanation: The only possible good partition is: ([1,1,1,1]).
#
# Example 3:
#
# Input: nums = [1,2,1,3]
# Output: 2
# Explanation: The 2 possible good partitions are: ([1,2,1], [3]) and
# ([1,2,1,3]).
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def numberOfGoodPartitions(self, nums: List[int]) -> int:
        """
        Interview explanation:
        A good partition never splits a value across parts: each value's first..last
        occurrence must lie in one segment. Independent segments multiply choices.

        Algorithm:
        - Record last index of each value. Sweep left→right, extend current segment
          end to last[nums[i]]. When i == end and not the final index, we may cut
          after i (×2). Answer is 2^(cuts) mod 1e9+7.

        Complexity: O(n) time, O(n) space.
        """
        MOD = 10**9 + 7
        last = {x: i for i, x in enumerate(nums)}
        ans = 1
        end = 0
        n = len(nums)
        for i, x in enumerate(nums):
            end = max(end, last[x])
            if i == end and i < n - 1:
                ans = ans * 2 % MOD
        return ans

    def numberOfGoodPartitions_segments(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: merge forced intervals [first, last] per value, then 2^(g-1).

        Algorithm:
        - Build intervals, sort/merge overlapping, let g = merged count; return 2^(g-1).

        Complexity: O(n log n) time, O(n) space.
        """
        MOD = 10**9 + 7
        first, last = {}, {}
        for i, x in enumerate(nums):
            if x not in first:
                first[x] = i
            last[x] = i
        intervals = sorted((first[x], last[x]) for x in first)
        merged = 0
        cur_end = -1
        for l, r in intervals:
            if l > cur_end:
                merged += 1
                cur_end = r
            else:
                cur_end = max(cur_end, r)
        return pow(2, merged - 1, MOD)
# @lc code=end
