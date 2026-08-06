#
# @lc app=leetcode id=2862 lang=python3
#
# [2862] Maximum Element-Sum of a Complete Subset of Indices
#
# https://leetcode.com/problems/maximum-element-sum-of-a-complete-subset-of-indices/description/
#
# algorithms
# Hard (43.42%)
# Likes:    236
# Dislikes: 59
# Total Accepted:    9.9K
# Total Submissions: 22.9K
# Testcase Example:  "[8,7,3,5,7,2,4,9]"
#
#
# You are given a 1-indexed array nums. Your task is to select a complete
# subset from nums where every pair of selected indices multiplied is a
# perfect square,. i. e. if you select a_i and a_j, i * j must be a
# perfect square.
#
# Return the sum of the complete subset with the maximum sum.
#
# Example 1:
#
# Input: nums = [8,7,3,5,7,2,4,9]
#
# Output: 16
#
# Explanation:
#
# We select elements at indices 2 and 8 and 2 * 8 is a perfect square.
#
# Example 2:
#
# Input: nums = [8,10,3,8,1,13,7,9,4]
#
# Output: 20
#
# Explanation:
#
# We select elements at indices 1, 4, and 9. 1 * 4, 1 * 9, 4 * 9 are
# perfect squares.
#
# Constraints:
#
# 1 <= n == nums.length <= 10^4
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def maximumSum(self, nums: List[int]) -> int:
        """
        Interview explanation:
        1-indexed nums; a complete index subset requires every pair product is a perfect
        square. Maximize sum of selected values.

        Algorithm:
        - Indices share a square-free kernel iff pairwise products are squares.
        - For each i, sum nums[i*j*j - 1] over j with i*j*j <= n; take max over i.
          (Full groups appear when i is square-free; others are subsets.)

        Complexity: O(n log n) time, O(1) extra space.
        """
        n = len(nums)
        ans = 0
        for i in range(1, n + 1):
            cur = 0
            j = 1
            while i * j * j <= n:
                cur += nums[i * j * j - 1]
                j += 1
            ans = max(ans, cur)
        return ans

    def maximumSum_by_kernel(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: explicitly group by square-free kernel of each index.

        Algorithm:
        - Strip square factors from index; accumulate nums into kernel buckets; max.

        Complexity: O(n sqrt n) naive factoring, O(n) space.
        """
        from collections import defaultdict

        n = len(nums)
        groups: dict[int, int] = defaultdict(int)
        for idx in range(1, n + 1):
            x = idx
            core = 1
            d = 2
            while d * d <= x:
                while x % (d * d) == 0:
                    x //= d * d
                if x % d == 0:
                    core *= d
                    x //= d
                d += 1
            if x > 1:
                core *= x
            groups[core] += nums[idx - 1]
        return max(groups.values())
# @lc code=end
