#
# @lc app=leetcode id=2488 lang=python3
#
# [2488] Count Subarrays With Median K
#
# https://leetcode.com/problems/count-subarrays-with-median-k/description/
#
# algorithms
# Hard (49.19%)
# Likes:    672
# Dislikes: 17
# Total Accepted:    21.9K
# Total Submissions: 44.6K
# Testcase Example:  "[3,2,1,4,5]\n4"
#
# You are given an array nums of size n consisting of distinct integers from 1
# to n and a positive integer k.
#
# Return the number of non-empty subarrays in nums that have a median equal to
# k.
#
# Note:
#
#
# The median of an array is the middle element after sorting the array in
# ascending order. If the array is of even length, the median is the left middle
# element.
#
#
#
#
# For example, the median of [2,3,1,4] is 2, and the median of [8,4,3,5,1] is 4.
#
#
#
#
#
#
# A subarray is a contiguous part of an array.
#
#
#
# Example 1:
#
# Input: nums = [3,2,1,4,5], k = 4
# Output: 3
# Explanation: The subarrays that have a median equal to 4 are: [4], [4,5] and
# [1,4,5].
#
# Example 2:
#
# Input: nums = [2,3,1], k = 3
# Output: 1
# Explanation: [3] is the only subarray that has a median equal to 3.
#
#
#
# Constraints:
#
#
# n == nums.length
#
#
# 1 <= n <= 10^5
#
#
# 1 <= nums[i], k <= n
#
#
# The integers in nums are distinct.
#

# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def countSubarrays(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Count subarrays whose median is k (odd length: middle; even: left of
        two middles after sort — here median means the ((len+1)//2)-th smallest).

        Algorithm:
        - Transform: >k -> +1, <k -> -1, ==k -> 0. Count balance prefixes where
          balance is 0 or 1 with odd/even rules around index of k.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        idx = nums.index(k)
        cnt = defaultdict(int)
        cnt[0] = 1
        bal = 0
        # left side including k
        for i in range(idx - 1, -1, -1):
            bal += 1 if nums[i] > k else -1
            cnt[bal] += 1
        ans = 0
        bal = 0
        for i in range(idx, n):
            if i != idx:
                bal += 1 if nums[i] > k else -1
            # median k iff #greater == #less or #greater == #less+1
            ans += cnt[bal] + cnt[bal - 1]
        return ans
# @lc code=end

