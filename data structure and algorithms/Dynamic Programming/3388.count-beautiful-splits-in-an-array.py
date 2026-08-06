#
# @lc app=leetcode id=3388 lang=python3
#
# [3388] Count Beautiful Splits in an Array
#
# https://leetcode.com/problems/count-beautiful-splits-in-an-array/description/
#
# algorithms
# Medium (19.03%)
# Likes:    109
# Dislikes: 25
# Total Accepted:    8.5K
# Total Submissions: 44.5K
# Testcase Example:  "[1,1,2,1]"
#
#
# You are given an array nums.
#
# A split of an array nums is beautiful if:
#
# The array nums is split into three subarrays: nums1, nums2, and nums3,
# such that nums can be formed by concatenating nums1, nums2, and nums3 in
# that order.
#
# The subarray nums1 is a prefix of nums2 OR nums2 is a prefix of nums3.
#
# Return the number of ways you can make this split.
#
# Example 1:
#
# Input: nums = [1,1,2,1]
#
# Output: 2
#
# Explanation:
#
# The beautiful splits are:
#
# A split with nums1 = [1], nums2 = [1,2], nums3 = [1].
#
# A split with nums1 = [1], nums2 = [1], nums3 = [2,1].
#
# Example 2:
#
# Input: nums = [1,2,3,4]
#
# Output: 0
#
# Explanation:
#
# There are 0 beautiful splits.
#
# Constraints:
#
# 1 <= nums.length <= 5000
#
# 0 <= nums[i] <= 50
#

# @lc code=start

from typing import List


class Solution:
    def beautifulSplits(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Split into nums1|nums2|nums3 where nums1 prefixes nums2, or nums2 prefixes
        nums3. Z-function / LCP table answers prefix checks in O(1) after O(n^2).

        Algorithm:
        - lcp[i][j] = longest common prefix of nums[i:] and nums[j:].
        - For splits (i, j): count if (lcp[0][i] >= i and j-i >= i) or
          (lcp[i][j] >= j-i).

        Complexity: O(n^2) time, O(n^2) space.
        """
        n = len(nums)
        lcp = [[0] * n for _ in range(n)]
        for i in range(n - 1, -1, -1):
            for j in range(n - 1, i, -1):
                if nums[i] == nums[j]:
                    lcp[i][j] = 1 + (lcp[i + 1][j + 1] if j + 1 < n else 0)
        ans = 0
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                if (lcp[0][i] >= i and j - i >= i) or lcp[i][j] >= j - i:
                    ans += 1
        return ans

    def beautifulSplits_z(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate classic tool: Z-array from index 0 and from each split point i.

        Algorithm:
        - z0 = Z(nums); for each i, zi = Z(nums[i:]).
        - Same predicate using z0[i] and zi[j-i].

        Complexity: O(n^2) time, O(n) space.
        """
        def z_function(s: List[int]) -> List[int]:
            z = [0] * len(s)
            l = r = 0
            for i in range(1, len(s)):
                if i <= r:
                    z[i] = min(r - i + 1, z[i - l])
                while i + z[i] < len(s) and s[z[i]] == s[i + z[i]]:
                    z[i] += 1
                if i + z[i] - 1 > r:
                    l, r = i, i + z[i] - 1
            return z

        n = len(nums)
        z0 = z_function(nums)
        ans = 0
        for i in range(1, n - 1):
            zi = z_function(nums[i:])
            for j in range(i + 1, n):
                if (z0[i] >= i and j - i >= i) or zi[j - i] >= j - i:
                    ans += 1
        return ans
# @lc code=end
