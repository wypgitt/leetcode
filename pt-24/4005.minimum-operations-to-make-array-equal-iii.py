#
# @lc app=leetcode id=4005 lang=python3
#
# [4005] Minimum Operations to Make Array Equal III
#
# https://leetcode.com/problems/minimum-operations-to-make-array-equal-iii/description/
#
# algorithms
# Hard (24.97%)
# Likes:    0
# Dislikes: 2
# Total Accepted:    191
# Total Submissions: 765
# Testcase Example:  "[6,12,8]"
#
#
# You are given an integer array nums.
#
# In one operation, you may choose any element nums[i] and perform one of
# the following:
#
# Multiply nums[i] by an integer k, where k >= 2.
#
# Divide nums[i] by an integer k, where 2 <= k < nums[i], provided that
# nums[i] is divisible by k.
#
# Return the minimum number of operations required to make all elements of
# nums equal.
#
# Example 1:
#
# Input: nums = [6,12,8]
#
# Output: 3
#
# Explanation:
#
# We can perform following operates to make all numbers to 6:
#
# Divide nums[1] = 12 by 2 to get 6.
#
# Divide nums[2] = 8 by 4 to get 2.
#
# Multiply nums[2] = 2 by 3 to get 6.
#
# Example 2:
#
# Input: nums = [5,15,20]
#
# Output: 2
#
# Explanation:
#
# We can perform following operates to make all numbers to 5:
#
# Divide nums[1] = 15 by 3 to get 5.
#
# Divide nums[2] = 20 by 4 to get 5.
#
# Example 3:
#
# Input: nums = [7,7,7]
#
# Output: 0
#
# Explanation:
#
# All elements are already equal, so no operations are needed.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^​​​​​​​9
#

# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def minOperations(self, nums: List[int]) -> int:
        """
        Interview explanation:
        One multiply or divide by any valid k costs 1, so any x can become any
        T≥2 in at most 2 ops (via lcm). Same bit-length values never properly
        divide each other, so within a bit-length bucket unrelated pairs cost 2.

        Algorithm:
        - Group values by bit_length; all-ones is already equal → 0.
        - Candidate targets = strict majority value in each bucket (bit_length>1).
        - Score each candidate: 0/1/2 per element by equality / divisibility.
        - Fallback answer n (send everything to a common multiple).

        Complexity: O(n · C) time with tiny C (#candidates), O(n) space.
        """
        cnt: dict[int, dict[int, int]] = defaultdict(lambda: defaultdict(int))
        for x in nums:
            cnt[x.bit_length()][x] += 1
        if cnt[1].get(1, 0) == len(nums):
            return 0

        candidates = []
        for length, bucket in cnt.items():
            if length == 1:
                continue
            total = sum(bucket.values())
            for x, c in bucket.items():
                if total - 2 * c >= 0:
                    continue
                candidates.append(x)
                break

        result = len(nums)
        for target in candidates:
            ops = 0
            for x in nums:
                if x == target:
                    continue
                ops += 1 if (x % target == 0 or target % x == 0) else 2
            result = min(result, ops)
        return result
# @lc code=end
