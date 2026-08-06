#
# @lc app=leetcode id=1775 lang=python3
#
# [1775] Equal Sum Arrays With Minimum Number of Operations
#
# https://leetcode.com/problems/equal-sum-arrays-with-minimum-number-of-operations/description/
#
# algorithms
# Medium (54.74%)
# Likes:    975
# Dislikes: 50
# Total Accepted:    36.7K
# Total Submissions: 67.0K
# Testcase Example:  "[1,2,3,4,5,6]"
#
# You are given two arrays of integers nums1 and nums2, possibly of different
# lengths. The values in the arrays are between 1 and 6, inclusive.
#
# In one operation, you can change any integer's value in any of the arrays to
# any value between 1 and 6, inclusive.
#
# Return the minimum number of operations required to make the sum of values in
# nums1 equal to the sum of values in nums2. Return -1 if it is not possible to
# make the sum of the two arrays equal.
#
# Example 1:
#
# Input: nums1 = [1,2,3,4,5,6], nums2 = [1,1,2,2,2,2]
# Output: 3
# Explanation: You can make the sums of nums1 and nums2 equal with 3
# operations. All indices are 0-indexed.
# - Change nums2[0] to 6. nums1 = [1,2,3,4,5,6], nums2 = [6,1,2,2,2,2].
# - Change nums1[5] to 1. nums1 = [1,2,3,4,5,1], nums2 = [6,1,2,2,2,2].
# - Change nums1[2] to 2. nums1 = [1,2,2,4,5,1], nums2 = [6,1,2,2,2,2].
#
# Example 2:
#
# Input: nums1 = [1,1,1,1,1,1,1], nums2 = [6]
# Output: -1
# Explanation: There is no way to decrease the sum of nums1 or to increase the
# sum of nums2 to make them equal.
#
# Example 3:
#
# Input: nums1 = [6,6], nums2 = [1]
# Output: 3
# Explanation: You can make the sums of nums1 and nums2 equal with 3
# operations. All indices are 0-indexed.
# - Change nums1[0] to 2. nums1 = [2,6], nums2 = [1].
# - Change nums1[1] to 2. nums1 = [2,2], nums2 = [1].
# - Change nums2[0] to 4. nums1 = [2,2], nums2 = [4].
#
# Constraints:
#
# 1 <= nums1.length, nums2.length <= 10^5
#
# 1 <= nums1[i], nums2[i] <= 6
#

# @lc code=start
from typing import List


class Solution:
    def minOperations(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        Change any element to any in 1..6 (1 op). Equalize sums. If impossible
        (sum ranges don't overlap) return -1. WLOG sum1 < sum2; greedily reduce
        the gap by largest available increase on nums1 or decrease on nums2.

        Algorithm:
        - If sum ranges disjoint: -1.
        - freq of (6-x) for smaller-sum array and (x-1) for larger; greedily
          apply largest gains until gap closed.

        Complexity: O(n+m) time, O(1) space.
        """
        if len(nums1) * 6 < len(nums2) * 1 or len(nums2) * 6 < len(nums1) * 1:
            return -1
        s1, s2 = sum(nums1), sum(nums2)
        if s1 == s2:
            return 0
        if s1 > s2:
            nums1, nums2 = nums2, nums1
            s1, s2 = s2, s1
        # need to increase s1 or decrease s2 by gap = s2-s1
        gap = s2 - s1
        # gains: increasing x→6 gives 6-x; decreasing y→1 gives y-1
        gains = [0] * 6
        for x in nums1:
            gains[6 - x] += 1
        for y in nums2:
            gains[y - 1] += 1
        ops = 0
        for g in range(5, 0, -1):
            while gains[g] and gap > 0:
                gap -= g
                gains[g] -= 1
                ops += 1
            if gap <= 0:
                return ops
        return ops
# @lc code=end
