#
# @lc app=leetcode id=2576 lang=python3
#
# [2576] Find the Maximum Number of Marked Indices
#
# https://leetcode.com/problems/find-the-maximum-number-of-marked-indices/description/
#
# algorithms
# Medium (41.53%)
# Likes:    606
# Dislikes: 29
# Total Accepted:    28.5K
# Total Submissions: 68.5K
# Testcase Example:  "[3,5,2,4]"
#
# You are given a 0-indexed integer array nums.
#
# Initially, all of the indices are unmarked. You are allowed to make this
# operation any number of times:
#
#
# Pick two different unmarked indices i and j such that 2 * nums[i] <= nums[j],
# then mark i and j.
#
# Return the maximum possible number of marked indices in nums using the above
# operation any number of times.
#
#
#
# Example 1:
#
# Input: nums = [3,5,2,4]
# Output: 2
# Explanation: In the first operation: pick i = 2 and j = 1, the operation is
# allowed because 2 * nums[2] <= nums[1]. Then mark index 2 and 1.
# It can be shown that there's no other valid operation so the answer is 2.
#
# Example 2:
#
# Input: nums = [9,2,5,4]
# Output: 4
# Explanation: In the first operation: pick i = 3 and j = 0, the operation is
# allowed because 2 * nums[3] <= nums[0]. Then mark index 3 and 0.
# In the second operation: pick i = 1 and j = 2, the operation is allowed
# because 2 * nums[1] <= nums[2]. Then mark index 1 and 2.
# Since there is no other operation, the answer is 4.
#
# Example 3:
#
# Input: nums = [7,6,8]
# Output: 0
# Explanation: There is no valid operation to do, so the answer is 0.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def maxNumOfMarkedIndices(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Pair indices so that 2*nums[i] <= nums[j]; maximize marked count (2 * pairs).

        Algorithm:
        - Sort; two pointers pair from the smaller half into the larger half.

        Complexity: O(n log n) time, O(1)/O(n) space.
        """
        nums.sort()
        n = len(nums)
        i = 0
        for j in range((n + 1) // 2, n):
            if 2 * nums[i] <= nums[j]:
                i += 1
        return i * 2

    def maxNumOfMarkedIndices_binary_search(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Binary search the number of pairs; verify k smallest pair with k largest.

        Algorithm:
        - Sort; for mid=k check 2*nums[i]<=nums[n-k+i] for all i.

        Complexity: O(n log n) time, O(1) extra space.
        """
        nums = sorted(nums)
        n = len(nums)
        lo, hi = 0, n // 2
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if all(2 * nums[i] <= nums[n - mid + i] for i in range(mid)):
                lo = mid
            else:
                hi = mid - 1
        return lo * 2
# @lc code=end
