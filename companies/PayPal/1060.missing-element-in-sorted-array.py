#
# @lc app=leetcode id=1060 lang=python3
#
# [1060] Missing Element in Sorted Array
#
# https://leetcode.com/problems/missing-element-in-sorted-array/description/
#
# algorithms
# Medium (59.73%)
# Likes:    1741
# Dislikes: 69
# Total Accepted:    171.3K
# Total Submissions: 286.9K
# Testcase Example:  "[4,7,9,10]\n1"
#
#
# Given an integer array nums which is sorted in ascending order and all
# of its elements are unique and given also an integer k, return the k^th
# missing number starting from the leftmost number of the array.
#
# Example 1:
#
# Input: nums = [4,7,9,10], k = 1
# Output: 5
# Explanation: The first missing number is 5.
#
# Example 2:
#
# Input: nums = [4,7,9,10], k = 3
# Output: 8
# Explanation: The missing numbers are [5,6,8,...], hence the third
# missing number is 8.
#
# Example 3:
#
# Input: nums = [1,2,4], k = 3
# Output: 6
# Explanation: The missing numbers are [3,5,6,7,...], hence the third
# missing number is 6.
#
# Constraints:
#
# 1 <= nums.length <= 5 * 10^4
#
# 1 <= nums[i] <= 10^7
#
# nums is sorted in ascending order, and all the elements are unique.
#
# 1 <= k <= 10^8
#
# Follow up: Can you find a logarithmic time complexity (i.e., O(log(n)))
# solution?
#
# @lc code=start
from typing import List


class Solution:
    def missingElement(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Premium. Sorted unique nums; missing count before index i is
        nums[i]-nums[0]-i. Binary search largest i with missing(i) < k; answer
        is nums[i] + (k - missing(i)).

        Algorithm:
        - missing(i)=nums[i]-nums[0]-i
        - If missing(n-1)<k: return nums[-1]+(k-missing(n-1))
        - Binary search rightmost i with missing(i)<k

        Complexity: O(log n) time, O(1) space.
        """
        n = len(nums)

        def missing(i: int) -> int:
            return nums[i] - nums[0] - i

        if missing(n - 1) < k:
            return nums[-1] + k - missing(n - 1)
        lo, hi = 0, n - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if missing(mid) < k:
                lo = mid
            else:
                hi = mid - 1
        return nums[lo] + k - missing(lo)

    def missingElement_linear(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate linear scan: between nums[i] and nums[i+1] there are
        gap-1 missing; subtract from k until found.

        Algorithm:
        - For i: gap=nums[i+1]-nums[i]-1; if k<=gap return nums[i]+k else k-=gap
        - Return nums[-1]+k

        Complexity: O(n) time, O(1) space.
        """
        for i in range(len(nums) - 1):
            gap = nums[i + 1] - nums[i] - 1
            if k <= gap:
                return nums[i] + k
            k -= gap
        return nums[-1] + k
# @lc code=end
