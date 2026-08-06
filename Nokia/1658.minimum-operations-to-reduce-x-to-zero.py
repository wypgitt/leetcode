#
# @lc app=leetcode id=1658 lang=python3
#
# [1658] Minimum Operations to Reduce X to Zero
#
# https://leetcode.com/problems/minimum-operations-to-reduce-x-to-zero/description/
#
# algorithms
# Medium (40.77%)
# Likes:    5823
# Dislikes: 129
# Total Accepted:    242K
# Total Submissions: 592K
# Testcase Example:  "[1,1,4,2,3]"
#
# You are given an integer array nums and an integer x. In one operation, you
# can either remove the leftmost or the rightmost element from the array nums
# and subtract its value from x. Note that this modifies the array for future
# operations.
#
# Return the minimum number of operations to reduce x to exactly 0 if it is
# possible, otherwise, return -1.
#
# Example 1:
#
# Input: nums = [1,1,4,2,3], x = 5
# Output: 2
# Explanation: The optimal solution is to remove the last two elements to
# reduce x to zero.
#
# Example 2:
#
# Input: nums = [5,6,7,8,9], x = 4
# Output: -1
#
# Example 3:
#
# Input: nums = [3,2,20,1,1,3], x = 10
# Output: 5
# Explanation: The optimal solution is to remove the last three elements and
# the first two elements (5 operations in total) to reduce x to zero.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^4
#
# 1 <= x <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def minOperations(self, nums: List[int], x: int) -> int:
        """
        Interview explanation:
        Remove prefix/suffix summing to x → equivalently find longest subarray
        with sum = total-x; answer = n - that length (or -1).

        Algorithm (sliding window / two pointers):
        - target = sum(nums)-x; if target<0 return -1; if 0 return n.
        - Expand right; shrink left while sum>target; track max window = target.

        Complexity: O(n) time, O(1) space.
        """
        target = sum(nums) - x
        if target < 0:
            return -1
        if target == 0:
            return len(nums)
        left = cur = 0
        best = -1
        for right, v in enumerate(nums):
            cur += v
            while cur > target and left <= right:
                cur -= nums[left]
                left += 1
            if cur == target:
                best = max(best, right - left + 1)
        return -1 if best < 0 else len(nums) - best

    def minOperations_prefix(self, nums: List[int], x: int) -> int:
        """
        Interview explanation:
        Alternate: prefix sums + hashmap of prefix→index; for each right prefix
        look up prefix-target for longest middle; or search left/right removals.

        Algorithm:
        - Map prefix sum to index; find max length with sum total-x.

        Complexity: O(n) time, O(n) space.
        """
        target = sum(nums) - x
        if target < 0:
            return -1
        seen = {0: -1}
        cur = best = 0
        found = target == 0
        if found:
            best = 0
        for i, v in enumerate(nums):
            cur += v
            if cur not in seen:
                seen[cur] = i
            if cur - target in seen:
                found = True
                best = max(best, i - seen[cur - target])
        return -1 if not found else len(nums) - best
# @lc code=end
