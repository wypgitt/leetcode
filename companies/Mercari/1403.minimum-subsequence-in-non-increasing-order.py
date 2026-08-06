#
# @lc app=leetcode id=1403 lang=python3
#
# [1403] Minimum Subsequence in Non-Increasing Order
#
# https://leetcode.com/problems/minimum-subsequence-in-non-increasing-order/description/
#
# algorithms
# Easy (74.01%)
# Likes:    646
# Dislikes: 513
# Total Accepted:    95.5K
# Total Submissions: 129K
# Testcase Example:  "[4,3,10,9,8]"
#
# Given the array nums, obtain a subsequence of the array whose sum of elements
# is strictly greater than the sum of the non included elements in such
# subsequence.
#
# If there are multiple solutions, return the subsequence with minimum size and
# if there still exist multiple solutions, return the subsequence with the
# maximum total sum of all its elements. A subsequence of an array can be
# obtained by erasing some (possibly zero) elements from the array.
#
# Note that the solution with the given constraints is guaranteed to be unique.
# Also return the answer sorted in non-increasing order.
#
# Example 1:
#
# Input: nums = [4,3,10,9,8]
# Output: [10,9]
# Explanation: The subsequences [10,9] and [10,8] are minimal such that the sum
# of their elements is strictly greater than the sum of elements not included.
# However, the subsequence [10,9] has the maximum total sum of its elements.
#
# Example 2:
#
# Input: nums = [4,4,7,6,7]
# Output: [7,7,6]
# Explanation: The subsequence [7,7] has the sum of its elements equal to 14
# which is not strictly greater than the sum of elements not included (14 = 4 +
# 4 + 6). Therefore, the subsequence [7,6,7] is the minimal satisfying the
# conditions. Note the subsequence has to be returned in non-increasing order.
#
# Constraints:
#
# 1 <= nums.length <= 500
#
# 1 <= nums[i] <= 100
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def minSubsequence(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Need non-increasing subsequence whose sum > sum of remaining, of
        minimal length (then maximal elements). Greedily take largest numbers.

        Algorithm:
        (sort)
        - total=sum(nums); sort desc; accumulate until > total/2; return taken.

        Complexity: O(n log n) time, O(n) space.
        """
        total = sum(nums)
        nums_sorted = sorted(nums, reverse=True)
        ans, cur = [], 0
        for x in nums_sorted:
            ans.append(x)
            cur += x
            if cur > total - cur:
                return ans
        return ans

    def minSubsequence_heap(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate: max-heap repeatedly extract largest until sum condition holds.

        Algorithm:
        - Heapify negatives; pop until cur > total-cur.

        Complexity: O(n log n) time, O(n) space.
        """
        total = sum(nums)
        heap = [-x for x in nums]
        heapq.heapify(heap)
        ans, cur = [], 0
        while heap and cur <= total - cur:
            x = -heapq.heappop(heap)
            ans.append(x)
            cur += x
        return ans
# @lc code=end
