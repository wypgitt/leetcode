#
# @lc app=leetcode id=2616 lang=python3
#
# [2616] Minimize the Maximum Difference of Pairs
#
# https://leetcode.com/problems/minimize-the-maximum-difference-of-pairs/description/
#
# algorithms
# Medium (51.02%)
# Likes:    2946
# Dislikes: 331
# Total Accepted:    172.9K
# Total Submissions: 339K
# Testcase Example:  "[10,1,2,7,1,3]\n2"
#
# You are given a 0-indexed integer array nums and an integer p. Find p pairs of
# indices of nums such that the maximum difference amongst all the pairs is
# minimized. Also, ensure no index appears more than once amongst the p pairs.
#
# Note that for a pair of elements at the index i and j, the difference of this
# pair is |nums[i] - nums[j]|, where |x| represents the absolute value of x.
#
# Return the minimum maximum difference among all p pairs. We define the maximum
# of an empty set to be zero.
#
#
#
# Example 1:
#
# Input: nums = [10,1,2,7,1,3], p = 2
# Output: 1
# Explanation: The first pair is formed from the indices 1 and 4, and the second
# pair is formed from the indices 2 and 5.
# The maximum difference is max(|nums[1] - nums[4]|, |nums[2] - nums[5]|) =
# max(0, 1) = 1. Therefore, we return 1.
#
# Example 2:
#
# Input: nums = [4,2,1,2], p = 1
# Output: 0
# Explanation: Let the indices 1 and 3 form a pair. The difference of that pair
# is |2 - 2| = 0, which is the minimum we can attain.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 0 <= nums[i] <= 10^9
#
#
# 0 <= p <= (nums.length)/2
#

# @lc code=start
from typing import List


class Solution:
    def minimizeMax(self, nums: List[int], p: int) -> int:
        """
        Interview explanation:
        Form p disjoint pairs minimizing the maximum pairwise absolute difference.

        Algorithm:
        - Sort nums. Binary search the max allowed difference mid.
        - Greedily form non-overlapping adjacent pairs with diff ≤ mid; check ≥ p.

        Complexity: O(n log n + n log A) time, O(1)/O(n) space.
        """
        if p == 0:
            return 0
        nums.sort()
        n = len(nums)

        def can(mid: int) -> bool:
            cnt = i = 0
            while i + 1 < n:
                if nums[i + 1] - nums[i] <= mid:
                    cnt += 1
                    i += 2
                else:
                    i += 1
            return cnt >= p

        lo, hi = 0, nums[-1] - nums[0]
        while lo < hi:
            mid = (lo + hi) // 2
            if can(mid):
                hi = mid
            else:
                lo = mid + 1
        return lo
# @lc code=end
