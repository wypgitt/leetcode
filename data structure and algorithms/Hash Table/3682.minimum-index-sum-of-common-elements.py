#
# @lc app=leetcode id=3682 lang=python3
#
# [3682] Minimum Index Sum of Common Elements
#
# https://leetcode.com/problems/minimum-index-sum-of-common-elements/description/
#
# algorithms
# Medium (76.91%)
# Likes:    6
# Dislikes: 1
# Total Accepted:    816
# Total Submissions: 1.1K
# Testcase Example:  "[3,2,1]\n[1,3,1]"
#
#
# You are given two integer arrays nums1 and nums2 of equal length n.
#
# We define a pair of indices (i, j) as a good pair if nums1[i] ==
# nums2[j].
#
# Return the minimum index sum i + j among all possible good pairs. If no
# such pairs exist, return -1.
#
# Example 1:
#
# Input: nums1 = [3,2,1], nums2 = [1,3,1]
#
# Output: 1
#
# Explanation:
#
# Common elements between nums1 and nums2 are 1 and 3.
#
# For 3, [i, j] = [0, 1], giving an index sum of i + j = 1.
#
# For 1, [i, j] = [2, 0], giving an index sum of i + j = 2.
#
# The minimum index sum is 1.
#
# Example 2:
#
# Input: nums1 = [5,1,2], nums2 = [2,1,3]
#
# Output: 2
#
# Explanation:
#
# Common elements between nums1 and nums2 are 1 and 2.
#
# For 1, [i, j] = [1, 1], giving an index sum of i + j = 2.
#
# For 2, [i, j] = [2, 0], giving an index sum of i + j = 2.
#
# The minimum index sum is 2.
#
# Example 3:
#
# Input: nums1 = [6,4], nums2 = [7,8]
#
# Output: -1
#
# Explanation:
#
# Since no common elements between nums1 and nums2, the output is -1.
#
# Constraints:
#
# 1 <= nums1.length == nums2.length <= 10^5
#
# -10^5 <= nums1[i], nums2[i] <= 10^5
#

# @lc code=start

from typing import List


class Solution:
    def minimumSum(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        A good pair matches equal values; for each common value the best index
        sum uses each array's earliest occurrence of that value.

        Algorithm:
        - Map each value in nums2 to its first index.
        - Scan nums1; for shared values track min i + first_j.
        - Alternate: build first-index maps for both arrays and take min over
          intersection keys.

        Complexity: O(n) time, O(n) space.
        """
        first2 = {}
        for j, x in enumerate(nums2):
            if x not in first2:
                first2[x] = j
        ans = float('inf')
        for i, x in enumerate(nums1):
            if x in first2:
                ans = min(ans, i + first2[x])
        return -1 if ans == float('inf') else ans
# @lc code=end
