#
# @lc app=leetcode id=321 lang=python3
#
# [321] Create Maximum Number
#
# https://leetcode.com/problems/create-maximum-number/description/
#
# algorithms
# Hard (36.28%)
# Likes:    2159
# Dislikes: 377
# Total Accepted:    91.4K
# Total Submissions: 252K
# Testcase Example:  "[3,4,6,5]"
#
# You are given two integer arrays nums1 and nums2 of lengths m and n
# respectively. nums1 and nums2 represent the digits of two numbers. You are
# also given an integer k.
#
# Create the maximum number of length k <= m + n from digits of the two
# numbers. The relative order of the digits from the same array must be
# preserved.
#
# Return an array of the k digits representing the answer.
#
# Example 1:
#
# Input: nums1 = [3,4,6,5], nums2 = [9,1,2,5,8,3], k = 5
# Output: [9,8,6,5,3]
#
# Example 2:
#
# Input: nums1 = [6,7], nums2 = [6,0,4], k = 5
# Output: [6,7,6,0,4]
#
# Example 3:
#
# Input: nums1 = [3,9], nums2 = [8,9], k = 3
# Output: [9,8,9]
#
# Constraints:
#
# m == nums1.length
#
# n == nums2.length
#
# 1 <= m, n <= 500
#
# 0 <= nums1[i], nums2[i] <= 9
#
# 1 <= k <= m + n
#
# nums1 and nums2 do not have leading zeros.
#

# @lc code=start
from typing import List


class Solution:
    def maxNumber(self, nums1: List[int], nums2: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Build the max k-digit number by choosing i digits from nums1 and k-i
        from nums2 (monotonic stack subsequence), then merge greedily like
        merge-sort comparing remaining suffixes.

        Algorithm:
        - For i in valid range: pick max i-subsequence of nums1 and (k-i) of nums2.
        - Merge the two sequences by always taking the larger remaining suffix.
        - Track the global maximum merge.

        Complexity: O(k * (m+n)^2) time, O(k) space.
        """
        def max_subsequence(nums: List[int], t: int) -> List[int]:
            drop = len(nums) - t
            stack: List[int] = []
            for num in nums:
                while drop and stack and stack[-1] < num:
                    stack.pop()
                    drop -= 1
                stack.append(num)
            return stack[:t]

        def merge(a: List[int], b: List[int]) -> List[int]:
            res: List[int] = []
            i = j = 0
            while i < len(a) or j < len(b):
                if a[i:] > b[j:]:
                    res.append(a[i])
                    i += 1
                else:
                    res.append(b[j])
                    j += 1
            return res

        m, n = len(nums1), len(nums2)
        best: List[int] = []
        for i in range(max(0, k - n), min(k, m) + 1):
            cand = merge(max_subsequence(nums1, i), max_subsequence(nums2, k - i))
            if cand > best:
                best = cand
        return best
# @lc code=end
