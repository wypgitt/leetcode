#
# @lc app=leetcode id=1983 lang=python3
#
# [1983] Widest Pair of Indices With Equal Range Sum
#
# https://leetcode.com/problems/widest-pair-of-indices-with-equal-range-sum/description/
#
# algorithms
# Medium (54.09%)
# Likes:    104
# Dislikes: 3
# Total Accepted:    3.7K
# Total Submissions: 6.8K
# Testcase Example:  "[1,1,0,1]\n[0,1,1,0]"
#
#
# You are given two 0-indexed binary arrays nums1 and nums2. Find the
# widest pair of indices (i, j) such that i <= j and nums1[i] + nums1[i+1]
# + ... + nums1[j] == nums2[i] + nums2[i+1] + ... + nums2[j].
#
# The widest pair of indices is the pair with the largest distance between
# i and j. The distance between a pair of indices is defined as j - i + 1.
#
# Return the distance of the widest pair of indices. If no pair of indices
# meets the conditions, return 0.
#
# Example 1:
#
# Input: nums1 = [1,1,0,1], nums2 = [0,1,1,0]
# Output: 3
# Explanation:
# If i = 1 and j = 3:
# nums1[1] + nums1[2] + nums1[3] = 1 + 0 + 1 = 2.
# nums2[1] + nums2[2] + nums2[3] = 1 + 1 + 0 = 2.
# The distance between i and j is j - i + 1 = 3 - 1 + 1 = 3.
#
# Example 2:
#
# Input: nums1 = [0,1], nums2 = [1,1]
# Output: 1
# Explanation:
# If i = 1 and j = 1:
# nums1[1] = 1.
# nums2[1] = 1.
# The distance between i and j is j - i + 1 = 1 - 1 + 1 = 1.
#
# Example 3:
#
# Input: nums1 = [0], nums2 = [1]
# Output: 0
# Explanation:
# There are no pairs of indices that meet the requirements.
#
# Constraints:
#
# n == nums1.length == nums2.length
#
# 1 <= n <= 10^5
#
# nums1[i] is either 0 or 1.
#
# nums2[i] is either 0 or 1.
#
# @lc code=start
from typing import List


class Solution:
    def widestPairOfIndices(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        Premium. Max j-i such that sum(nums1[i..j]) == sum(nums2[i..j]), i.e.
        prefix of (nums1-nums2) equal at i-1 and j. Track first index of each
        prefix difference.

        Algorithm:
        - diff prefix p; map first occurrence of each p; ans = max i - first[p].

        Complexity: O(n) time, O(n) space.
        """
        first = {0: -1}
        p = 0
        ans = 0
        for i, (a, b) in enumerate(zip(nums1, nums2)):
            p += a - b
            if p in first:
                ans = max(ans, i - first[p])
            else:
                first[p] = i
        return ans

    def widestPairOfIndices_clarity(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        Alternate: build explicit difference array then same first-seen prefix map.

        Algorithm:
        - d[i]=nums1[i]-nums2[i]; scan prefix sums with hashmap of first index.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums1)
        d = [nums1[i] - nums2[i] for i in range(n)]
        seen = {0: -1}
        s = 0
        best = 0
        for i, x in enumerate(d):
            s += x
            if s in seen:
                best = max(best, i - seen[s])
            else:
                seen[s] = i
        return best
# @lc code=end

