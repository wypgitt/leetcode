#
# @lc app=leetcode id=2563 lang=python3
#
# [2563] Count the Number of Fair Pairs
#
# https://leetcode.com/problems/count-the-number-of-fair-pairs/description/
#
# algorithms
# Medium (52.60%)
# Likes:    2027
# Dislikes: 150
# Total Accepted:    242.3K
# Total Submissions: 460.6K
# Testcase Example:  "[0,1,7,4,4,5]\n3\n6"
#
# Given a 0-indexed integer array nums of size n and two integers lower and
# upper, return the number of fair pairs.
#
# A pair (i, j) is fair if:
#
#
# 0 <= i < j < n, and
#
#
# lower <= nums[i] + nums[j] <= upper
#
#
#
# Example 1:
#
# Input: nums = [0,1,7,4,4,5], lower = 3, upper = 6
# Output: 6
# Explanation: There are 6 fair pairs: (0,3), (0,4), (0,5), (1,3), (1,4), and
# (1,5).
#
# Example 2:
#
# Input: nums = [1,7,9,2,5], lower = 11, upper = 11
# Output: 1
# Explanation: There is a single fair pair: (2,3).
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# nums.length == n
#
#
# -10^9 <= nums[i] <= 10^9
#
#
# -10^9 <= lower <= upper <= 10^9
#

# @lc code=start
from typing import List
import bisect


class Solution:
    def countFairPairs(self, nums: List[int], lower: int, upper: int) -> int:
        """
        Interview explanation:
        Count pairs i<j with lower <= nums[i]+nums[j] <= upper.

        Algorithm:
        - Sort; for each i use bisect to count partners in [lower-nums[i], upper-nums[i]].

        Complexity: O(n log n) time, O(1)/O(n) space.
        """
        nums.sort()
        n = len(nums)
        ans = 0
        for i in range(n):
            lo = bisect.bisect_left(nums, lower - nums[i], i + 1, n)
            hi = bisect.bisect_right(nums, upper - nums[i], i + 1, n)
            ans += hi - lo
        return ans

    def countFairPairs_two_pointers(self, nums: List[int], lower: int, upper: int) -> int:
        """
        Interview explanation:
        Count fair pairs via two sorted sweeps for upper and lower-1.

        Algorithm:
        - Sort; helper counts pairs with sum <= x using two pointers; answer f(upper)-f(lower-1).

        Complexity: O(n log n) time, O(1) extra space.
        """
        nums.sort()

        def count_le(x: int) -> int:
            i, j = 0, len(nums) - 1
            res = 0
            while i < j:
                if nums[i] + nums[j] <= x:
                    res += j - i
                    i += 1
                else:
                    j -= 1
            return res

        return count_le(upper) - count_le(lower - 1)
# @lc code=end
