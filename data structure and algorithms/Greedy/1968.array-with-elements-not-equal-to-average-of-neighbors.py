#
# @lc app=leetcode id=1968 lang=python3
#
# [1968] Array With Elements Not Equal to Average of Neighbors
#
# https://leetcode.com/problems/array-with-elements-not-equal-to-average-of-neighbors/description/
#
# algorithms
# Medium (50.84%)
# Likes:    669
# Dislikes: 59
# Total Accepted:    51.6K
# Total Submissions: 101K
# Testcase Example:  "[1,2,3,4,5]"
#
# You are given a 0-indexed array nums of distinct integers. You want to
# rearrange the elements in the array such that every element in the rearranged
# array is not equal to the average of its neighbors.
#
# More formally, the rearranged array should have the property such that for
# every i in the range 1 <= i < nums.length - 1, (nums[i-1] + nums[i+1]) / 2 is
# not equal to nums[i].
#
# Return any rearrangement of nums that meets the requirements.
#
# Example 1:
#
# Input: nums = [1,2,3,4,5]
# Output: [1,2,4,5,3]
# Explanation:
# When i=1, nums[i] = 2, and the average of its neighbors is (1+4) / 2 = 2.5.
# When i=2, nums[i] = 4, and the average of its neighbors is (2+5) / 2 = 3.5.
# When i=3, nums[i] = 5, and the average of its neighbors is (4+3) / 2 = 3.5.
#
# Example 2:
#
# Input: nums = [6,2,0,9,7]
# Output: [9,7,6,2,0]
# Explanation:
# When i=1, nums[i] = 7, and the average of its neighbors is (9+6) / 2 = 7.5.
# When i=2, nums[i] = 6, and the average of its neighbors is (7+2) / 2 = 4.5.
# When i=3, nums[i] = 2, and the average of its neighbors is (6+0) / 2 = 3.
# Note that the original array [6,2,0,9,7] also satisfies the conditions.
#
# Constraints:
#
# 3 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def rearrangeArray(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Rearrange so no nums[i] equals average of neighbors (no 2*a[i]=a[i-1]+a[i+1]).
        Sort then put small/large alternating, or swap when a local AP appears.

        Algorithm:
        - Sort; place smaller half on even indices, larger on odd (or reverse
          fill). Classic: sort then swap every adjacent pair.

        Complexity: O(n log n) time, O(n) space.
        """
        a = sorted(nums)
        n = len(a)
        for i in range(1, n, 2):
            a[i - 1], a[i] = a[i], a[i - 1]
        return a

    def rearrangeArray_swap(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate: sort, then for each middle index if AP, swap with next.

        Algorithm:
        - a=sorted(nums); for i in 1..n-2: if 2*a[i]==a[i-1]+a[i+1]: swap i,i+1.

        Complexity: O(n log n) time, O(n) space.
        """
        a = sorted(nums)
        for i in range(1, len(a) - 1):
            if 2 * a[i] == a[i - 1] + a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]
        return a
# @lc code=end

