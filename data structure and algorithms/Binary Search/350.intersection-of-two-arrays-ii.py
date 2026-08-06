#
# @lc app=leetcode id=350 lang=python3
#
# [350] Intersection of Two Arrays II
#
# https://leetcode.com/problems/intersection-of-two-arrays-ii/description/
#
# algorithms
# Easy (60.17%)
# Likes:    8257
# Dislikes: 1010
# Total Accepted:    1.8M
# Total Submissions: 3.0M
# Testcase Example:  "[1,2,2,1]"
#
# Given two integer arrays nums1 and nums2, return an array of their
# intersection. Each element in the result must appear as many times as it
# shows in both arrays and you may return the result in any order.
#
# Example 1:
#
# Input: nums1 = [1,2,2,1], nums2 = [2,2]
# Output: [2,2]
#
# Example 2:
#
# Input: nums1 = [4,9,5], nums2 = [9,4,9,8,4]
# Output: [4,9]
# Explanation: [9,4] is also accepted.
#
# Constraints:
#
# 1 <= nums1.length, nums2.length <= 1000
#
# 0 <= nums1[i], nums2[i] <= 1000
#
# Follow up:
#
# What if the given array is already sorted? How would you optimize your
# algorithm?
#
# What if nums1's size is small compared to nums2's size? Which algorithm is
# better?
#
# What if elements of nums2 are stored on disk, and the memory is limited such
# that you cannot load all elements into the memory at once?
#

# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def intersect(self, nums1: List[int], nums2: List[int]) -> List[int]:
        """
        Interview explanation:
        Multiset intersection via Counter: take min frequency of each shared
        key and emit that many copies.

        Algorithm:
        - Counter both (or one + scan the other); for each common key append
          min(c1, c2) copies.

        Complexity: O(m + n) time, O(min(m, n)) space.
        """
        if len(nums1) > len(nums2):
            nums1, nums2 = nums2, nums1
        count = Counter(nums1)
        res: List[int] = []
        for num in nums2:
            if count[num] > 0:
                res.append(num)
                count[num] -= 1
        return res
# @lc code=end
