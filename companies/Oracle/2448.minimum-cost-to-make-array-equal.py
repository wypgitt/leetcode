#
# @lc app=leetcode id=2448 lang=python3
#
# [2448] Minimum Cost to Make Array Equal
#
# https://leetcode.com/problems/minimum-cost-to-make-array-equal/description/
#
# algorithms
# Hard (46.86%)
# Likes:    2551
# Dislikes: 40
# Total Accepted:    80K
# Total Submissions: 170.6K
# Testcase Example:  "[1,3,5,2]\n[2,3,1,14]"
#
# You are given two 0-indexed arrays nums and cost consisting each of n positive
# integers.
#
# You can do the following operation any number of times:
#
#
# Increase or decrease any element of the array nums by 1.
#
# The cost of doing one operation on the i^th element is cost[i].
#
# Return the minimum total cost such that all the elements of the array nums
# become equal.
#
#
#
# Example 1:
#
# Input: nums = [1,3,5,2], cost = [2,3,1,14]
# Output: 8
# Explanation: We can make all the elements equal to 2 in the following way:
# - Increase the 0^th element one time. The cost is 2.
# - Decrease the 1^st element one time. The cost is 3.
# - Decrease the 2^nd element three times. The cost is 1 + 1 + 1 = 3.
# The total cost is 2 + 3 + 3 = 8.
# It can be shown that we cannot make the array equal with a smaller cost.
#
# Example 2:
#
# Input: nums = [2,2,2,2,2], cost = [4,2,8,1,3]
# Output: 0
# Explanation: All the elements are already equal, so no operations are needed.
#
#
#
# Constraints:
#
#
# n == nums.length == cost.length
#
#
# 1 <= n <= 10^5
#
#
# 1 <= nums[i], cost[i] <= 10^6
#
#
# Test cases are generated in a way that the output doesn't exceed 2^53-1
#

# @lc code=start
from typing import List


class Solution:
    def minCost(self, nums: List[int], cost: List[int]) -> int:
        """
        Interview explanation:
        Make all elements equal to some x; cost |nums[i]-x|*cost[i]. Minimize.

        Algorithm:
        - Weighted median: sort by value; first prefix with weight >= total/2.

        Complexity: O(n log n) time, O(n) space.
        """
        arr = sorted(zip(nums, cost))
        total = sum(cost)
        acc = 0
        median = arr[0][0]
        for v, c in arr:
            acc += c
            if acc >= (total + 1) // 2:
                median = v
                break
        return sum(abs(v - median) * c for v, c in arr)

    def minCost_binary_search(self, nums: List[int], cost: List[int]) -> int:
        """
        Interview explanation:
        Alternate binary search on convex cost over the value domain.

        Algorithm:
        - Move to side where f(mid) > f(mid+1) until convergence.

        Complexity: O(n log A) time, O(1) space.
        """
        def f(x: int) -> int:
            return sum(abs(v - x) * c for v, c in zip(nums, cost))

        lo, hi = min(nums), max(nums)
        while lo < hi:
            mid = (lo + hi) // 2
            if f(mid) < f(mid + 1):
                hi = mid
            else:
                lo = mid + 1
        return f(lo)
# @lc code=end
