#
# @lc app=leetcode id=2170 lang=python3
#
# [2170] Minimum Operations to Make the Array Alternating
#
# https://leetcode.com/problems/minimum-operations-to-make-the-array-alternating/description/
#
# algorithms
# Medium (35.83%)
# Likes:    628
# Dislikes: 344
# Total Accepted:    31.1K
# Total Submissions: 86.9K
# Testcase Example:  "[3,1,3,2,4,3]"
#
# You are given a 0-indexed array nums consisting of n positive integers.
#
# The array nums is called alternating if:
#
#
# nums[i - 2] == nums[i], where 2 <= i <= n - 1.
#
#
# nums[i - 1] != nums[i], where 1 <= i <= n - 1.
#
# In one operation, you can choose an index i and change nums[i] into any
# positive integer.
#
# Return the minimum number of operations required to make the array
# alternating.
#
#
#
# Example 1:
#
# Input: nums = [3,1,3,2,4,3]
# Output: 3
# Explanation:
# One way to make the array alternating is by converting it to [3,1,3,1,3,1].
# The number of operations required in this case is 3.
# It can be proven that it is not possible to make the array alternating in less
# than 3 operations.
#
# Example 2:
#
# Input: nums = [1,2,2,2,2]
# Output: 2
# Explanation:
# One way to make the array alternating is by converting it to [1,2,1,2,1].
# The number of operations required in this case is 2.
# Note that the array cannot be converted to [2,2,2,2,2] because in this case
# nums[0] == nums[1] which violates the conditions of an alternating array.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def minimumOperations(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Make array alternating: nums[i] == nums[i+2] for all valid i, and
        nums[i] != nums[i+1]. Change any element to any value costs 1. Minimize
        operations (= n - max kept).

        Algorithm:
        (frequency on even/odd indices)
        - Count freqs on even and odd positions.
        - Try top-2 candidates for even and odd; if values differ, keep both
          maxes; if same, try max_even+second_odd or second_even+max_odd.
        - ops = n - best kept.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        if n == 1:
            return 0
        even = Counter(nums[i] for i in range(0, n, 2))
        odd = Counter(nums[i] for i in range(1, n, 2))

        def top2(cnt: Counter) -> List[tuple]:
            items = cnt.most_common(2)
            while len(items) < 2:
                items.append((None, 0))
            return items

        e1, e2 = top2(even)
        o1, o2 = top2(odd)
        if e1[0] != o1[0]:
            keep = e1[1] + o1[1]
        else:
            keep = max(e1[1] + o2[1], e2[1] + o1[1])
        return n - keep
# @lc code=end
