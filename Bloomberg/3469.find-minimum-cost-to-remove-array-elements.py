#
# @lc app=leetcode id=3469 lang=python3
#
# [3469] Find Minimum Cost to Remove Array Elements
#
# https://leetcode.com/problems/find-minimum-cost-to-remove-array-elements/description/
#
# algorithms
# Medium (22.33%)
# Likes:    156
# Dislikes: 11
# Total Accepted:    13.6K
# Total Submissions: 61.1K
# Testcase Example:  "[6,2,8,4]"
#
#
# You are given an integer array nums. Your task is to remove all elements
# from the array by performing one of the following operations at each
# step until nums is empty:
#
# Choose any two elements from the first three elements of nums and remove
# them. The cost of this operation is the maximum of the two elements
# removed.
#
# If fewer than three elements remain in nums, remove all the remaining
# elements in a single operation. The cost of this operation is the
# maximum of the remaining elements.
#
# Return the minimum cost required to remove all the elements.
#
# Example 1:
#
# Input: nums = [6,2,8,4]
#
# Output: 12
#
# Explanation:
#
# Initially, nums = [6, 2, 8, 4].
#
# In the first operation, remove nums[0] = 6 and nums[2] = 8 with a cost
# of max(6, 8) = 8. Now, nums = [2, 4].
#
# In the second operation, remove the remaining elements with a cost of
# max(2, 4) = 4.
#
# The cost to remove all elements is 8 + 4 = 12. This is the minimum cost
# to remove all elements in nums. Hence, the output is 12.
#
# Example 2:
#
# Input: nums = [2,1,3,3]
#
# Output: 5
#
# Explanation:
#
# Initially, nums = [2, 1, 3, 3].
#
# In the first operation, remove nums[0] = 2 and nums[1] = 1 with a cost
# of max(2, 1) = 2. Now, nums = [3, 3].
#
# In the second operation remove the remaining elements with a cost of
# max(3, 3) = 3.
#
# The cost to remove all elements is 2 + 3 = 5. This is the minimum cost
# to remove all elements in nums. Hence, the output is 5.
#
# Constraints:
#
# 1 <= nums.length <= 1000
#
# 1 <= nums[i] <= 10^6
#

# @lc code=start
import functools
from typing import List


class Solution:
    def minCost(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Always operate on the first three of the current sequence. One element
        may be deferred (the "last" kept from earlier). DP over (kept index,
        next index).

        Algorithm:
        - State dp(last, i): min cost with deferred nums[last] and suffix i..
        - From three candidates (last, i, i+1), try removing each pair; recurse.
        - Base: 1 or 2 elements left => max of them.

        Complexity: O(n^2) time/space (n <= 1000).
        """
        n = len(nums)

        @functools.lru_cache(None)
        def dp(last: int, i: int) -> int:
            if i == n:
                return nums[last]
            if i == n - 1:
                return max(nums[last], nums[i])
            a = max(nums[i], nums[i + 1]) + dp(last, i + 2)
            b = max(nums[last], nums[i]) + dp(i + 1, i + 2)
            c = max(nums[last], nums[i + 1]) + dp(i, i + 2)
            return min(a, b, c)

        return dp(0, 1)
# @lc code=end

