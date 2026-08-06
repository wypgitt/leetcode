#
# @lc app=leetcode id=2367 lang=python3
#
# [2367] Number of Arithmetic Triplets
#
# https://leetcode.com/problems/number-of-arithmetic-triplets/description/
#
# algorithms
# Easy (85.59%)
# Likes:    1405
# Dislikes: 98
# Total Accepted:    192.6K
# Total Submissions: 225K
# Testcase Example:  "[0,1,4,6,7,10]\n3"
#
# You are given a 0-indexed, strictly increasing integer array nums and a
# positive integer diff. A triplet (i, j, k) is an arithmetic triplet if the
# following conditions are met:
#
#
# i < j < k,
#
#
# nums[j] - nums[i] == diff, and
#
#
# nums[k] - nums[j] == diff.
#
# Return the number of unique arithmetic triplets.
#
#
#
# Example 1:
#
# Input: nums = [0,1,4,6,7,10], diff = 3
# Output: 2
# Explanation:
# (1, 2, 4) is an arithmetic triplet because both 7 - 4 == 3 and 4 - 1 == 3.
# (2, 4, 5) is an arithmetic triplet because both 10 - 7 == 3 and 7 - 4 == 3.
#
# Example 2:
#
# Input: nums = [4,5,6,7,8,9], diff = 2
# Output: 2
# Explanation:
# (0, 2, 4) is an arithmetic triplet because both 8 - 6 == 2 and 6 - 4 == 2.
# (1, 3, 5) is an arithmetic triplet because both 9 - 7 == 2 and 7 - 5 == 2.
#
#
#
# Constraints:
#
#
# 3 <= nums.length <= 200
#
#
# 0 <= nums[i] <= 200
#
#
# 1 <= diff <= 50
#
#
# nums is strictly increasing.
#

# @lc code=start

from typing import List


class Solution:
    def arithmeticTriplets(self, nums: List[int], diff: int) -> int:
        """
        Interview explanation:
        Count triplets i<j<k with nums[j]-nums[i]==nums[k]-nums[j]==diff.
        nums is strictly increasing.

        Algorithm:
        - Set membership: for each x count if x-diff and x-2*diff present.

        Complexity: O(n) time, O(n) space.
        """
        s = set(nums)
        return sum(1 for x in nums if x - diff in s and x - 2 * diff in s)

    def arithmeticTriplets_three_pointers(self, nums: List[int], diff: int) -> int:
        """
        Interview explanation:
        Alternate: three pointers on sorted unique array.

        Algorithm:
        - For each j advance i/k to match diffs.

        Complexity: O(n) time, O(1) space.
        """
        n = len(nums)
        ans = i = k = 0
        for j in range(n):
            while i < j and nums[j] - nums[i] > diff:
                i += 1
            while k < n and nums[k] - nums[j] < diff:
                k += 1
            if i < j and k < n and nums[j] - nums[i] == diff and nums[k] - nums[j] == diff:
                ans += 1
        return ans
# @lc code=end
