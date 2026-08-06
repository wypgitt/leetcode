#
# @lc app=leetcode id=3400 lang=python3
#
# [3400] Maximum Number of Matching Indices After Right Shifts
#
# https://leetcode.com/problems/maximum-number-of-matching-indices-after-right-shifts/description/
#
# algorithms
# Medium (84.97%)
# Likes:    15
# Dislikes: 1
# Total Accepted:    1.8K
# Total Submissions: 2.1K
# Testcase Example:  "[3,1,2,3,1,2]\n[1,2,3,1,2,3]"
#
#
# You are given two integer arrays, nums1 and nums2, of the same length.
#
# An index i is considered matching if nums1[i] == nums2[i].
#
# Return the maximum number of matching indices after performing any
# number of right shifts on nums1.
#
# A right shift is defined as shifting the element at index i to index (i
# + 1) % n, for all indices.
#
# Example 1:
#
# Input: nums1 = [3,1,2,3,1,2], nums2 = [1,2,3,1,2,3]
#
# Output: 6
#
# Explanation:
#
# If we right shift nums1 2 times, it becomes [1, 2, 3, 1, 2, 3]. Every
# index matches, so the output is 6.
#
# Example 2:
#
# Input: nums1 = [1,4,2,5,3,1], nums2 = [2,3,1,2,4,6]
#
# Output: 3
#
# Explanation:
#
# If we right shift nums1 3 times, it becomes [5, 3, 1, 1, 4, 2]. Indices
# 1, 2, and 4 match, so the output is 3.
#
# Constraints:
#
# nums1.length == nums2.length
#
# 1 <= nums1.length, nums2.length <= 3000
#
# 1 <= nums1[i], nums2[i] <= 10^9
#

# @lc code=start

from typing import List


class Solution:
    def maximumMatchingIndices(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        Right-shifting nums1 by s places maps old index j to (j+s)%n. Count
        matches against nums2 over all s; n <= 3000 so O(n^2) is fine.

        Algorithm:
        - For each shift s in 0..n-1, count i where nums1[(i-s)%n] == nums2[i].
        - Return the maximum count.

        Complexity: O(n^2) time, O(1) space.
        """
        n = len(nums1)
        ans = 0
        for s in range(n):
            cnt = sum(1 for i in range(n) if nums1[(i - s) % n] == nums2[i])
            ans = max(ans, cnt)
        return ans
# @lc code=end
