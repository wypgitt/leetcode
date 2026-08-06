#
# @lc app=leetcode id=698 lang=python3
#
# [698] Partition to K Equal Sum Subsets
#
# https://leetcode.com/problems/partition-to-k-equal-sum-subsets/description/
#
# algorithms
# Medium (38.8%)
# Likes:    7614
# Dislikes: 557
# Total Accepted:    355K
# Total Submissions: 916K
# Testcase Example:  "[4,3,2,3,5,2,1]"
#
# Given an integer array nums and an integer k, return true if it is possible
# to divide this array into k non-empty subsets whose sums are all equal.
#
# Example 1:
#
# Input: nums = [4,3,2,3,5,2,1], k = 4
# Output: true
# Explanation: It is possible to divide it into 4 subsets (5), (1, 4), (2,3),
# (2,3) with equal sums.
#
# Example 2:
#
# Input: nums = [1,2,3,4], k = 3
# Output: false
#
# Constraints:
#
# 1 <= k <= nums.length <= 16
#
# 1 <= nums[i] <= 10^4
#
# The frequency of each element is in the range [1, 4].
#

# @lc code=start
from typing import List


class Solution:
    def canPartitionKSubsets(self, nums: List[int], k: int) -> bool:
        """
        Interview explanation:
        Partition into k subsets with equal sum. Backtrack: target = total/k;
        assign numbers into current bucket until full, then next bucket. Sort
        descending and prune to cut search.

        Algorithm:
        - If total % k != 0 fail. Sort desc. used[] bitmask/array.
        - dfs(start, k_left, remain): if k_left==0 True; if remain==0 start next
          bucket; try unused nums[i] <= remain.

        Complexity: O(k * 2^n) worst-case backtrack, O(n) space.
        """
        total = sum(nums)
        if k == 0 or total % k != 0:
            return False
        target = total // k
        nums.sort(reverse=True)
        if nums[0] > target:
            return False
        n = len(nums)
        used = [False] * n

        def dfs(start: int, k_left: int, remain: int) -> bool:
            if k_left == 1:
                return True
            if remain == 0:
                return dfs(0, k_left - 1, target)
            for i in range(start, n):
                if used[i] or nums[i] > remain:
                    continue
                if i > 0 and nums[i] == nums[i - 1] and not used[i - 1]:
                    continue
                used[i] = True
                if dfs(i + 1, k_left, remain - nums[i]):
                    return True
                used[i] = False
            return False

        return dfs(0, k, target)
# @lc code=end
