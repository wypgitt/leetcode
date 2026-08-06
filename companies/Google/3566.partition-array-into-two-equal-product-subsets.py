#
# @lc app=leetcode id=3566 lang=python3
#
# [3566] Partition Array into Two Equal Product Subsets
#
# https://leetcode.com/problems/partition-array-into-two-equal-product-subsets/description/
#
# algorithms
# Medium (35.32%)
# Likes:    92
# Dislikes: 21
# Total Accepted:    36K
# Total Submissions: 102.1K
# Testcase Example:  "[3,1,6,8,4]\n24"
#
#
# You are given an integer array nums containing distinct positive
# integers and an integer target.
#
# Determine if you can partition nums into two non-empty disjoint subsets,
# with each element belonging to exactly one subset, such that the product
# of the elements in each subset is equal to target.
#
# Return true if such a partition exists and false otherwise.
#
# A subset of an array is a selection of elements of the array.
#
# Example 1:
#
# Input: nums = [3,1,6,8,4], target = 24
#
# Output: true
#
# Explanation: The subsets [3, 8] and [1, 6, 4] each have a product of 24.
# Hence, the output is true.
#
# Example 2:
#
# Input: nums = [2,5,3,7], target = 15
#
# Output: false
#
# Explanation: There is no way to partition nums into two non-empty
# disjoint subsets such that both subsets have a product of 15. Hence, the
# output is false.
#
# Constraints:
#
# 3 <= nums.length <= 12
#
# 1 <= target <= 10^15
#
# 1 <= nums[i] <= 100
#
# All elements of nums are distinct.
#

# @lc code=start

from typing import List


class Solution:
    def checkEqualPartitions(self, nums: List[int], target: int) -> bool:
        """
        Interview explanation:
        Both subsets must multiply to target, so the full product must be
        target^2. With n ≤ 12, search for a nonempty proper subset with product
        target (the complement then also has product target).

        Algorithm:
        - Reject if any nums[i] does not divide target, or total product != target^2.
        - DFS over take/skip choices; succeed when product == target with 0 < taken < n.

        Complexity: O(2^n) time, O(n) space.
        """
        n = len(nums)
        for x in nums:
            if target % x != 0:
                return False
        total = 1
        for x in nums:
            total *= x
            if total > target * target:
                return False
        if total != target * target:
            return False

        def dfs(i: int, prod: int, taken: int) -> bool:
            if taken and prod == target and taken < n:
                return True
            if i == n or prod > target:
                return False
            if dfs(i + 1, prod * nums[i], taken + 1):
                return True
            return dfs(i + 1, prod, taken)

        return dfs(0, 1, 0)

    def checkEqualPartitions_bitmask(self, nums: List[int], target: int) -> bool:
        """
        Interview explanation:
        Alternate: enumerate all nonempty proper bitmasks whose product equals
        target (complement product follows from total == target^2).

        Algorithm:
        - Same total check; for mask in 1..(2^n-2) multiply selected elements.

        Complexity: O(2^n · n) time, O(1) space.
        """
        n = len(nums)
        total = 1
        for x in nums:
            if target % x != 0:
                return False
            total *= x
            if total > target * target:
                return False
        if total != target * target:
            return False
        for mask in range(1, (1 << n) - 1):
            p = 1
            ok = True
            for i in range(n):
                if mask & (1 << i):
                    p *= nums[i]
                    if p > target:
                        ok = False
                        break
            if ok and p == target:
                return True
        return False
# @lc code=end
