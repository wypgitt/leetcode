#
# @lc app=leetcode id=1995 lang=python3
#
# [1995] Count Special Quadruplets
#
# https://leetcode.com/problems/count-special-quadruplets/description/
#
# algorithms
# Easy (64.86%)
# Likes:    716
# Dislikes: 245
# Total Accepted:    65.6K
# Total Submissions: 101K
# Testcase Example:  "[1,2,3,6]"
#
# Given a 0-indexed integer array nums, return the number of distinct
# quadruplets (a, b, c, d) such that:
#
# nums[a] + nums[b] + nums[c] == nums[d], and
#
# a < b < c < d
#
# Example 1:
#
# Input: nums = [1,2,3,6]
# Output: 1
# Explanation: The only quadruplet that satisfies the requirement is (0, 1, 2,
# 3) because 1 + 2 + 3 == 6.
#
# Example 2:
#
# Input: nums = [3,3,6,4,5]
# Output: 0
# Explanation: There are no such quadruplets in [3,3,6,4,5].
#
# Example 3:
#
# Input: nums = [1,1,1,3,5]
# Output: 4
# Explanation: The 4 quadruplets that satisfy the requirement are:
# - (0, 1, 2, 3): 1 + 1 + 1 == 3
# - (0, 1, 3, 4): 1 + 1 + 3 == 5
# - (0, 2, 3, 4): 1 + 1 + 3 == 5
# - (1, 2, 3, 4): 1 + 1 + 3 == 5
#
# Constraints:
#
# 4 <= nums.length <= 50
#
# 1 <= nums[i] <= 100
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def countQuadruplets(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Count a+b+c=d with i<j<k<l. Brute O(n^4) ok for n<=50; better O(n^2)
        with hash of sums / two-pointer style from ends.

        Algorithm:
        - Scan c from right to left; freq holds values of indices > c as d.
        - For each a<b<c, add freq[nums[a]+nums[b]+nums[c]]; then freq[nums[c]]++.
        - (O(n^3) hash; n<=50. Brute O(n^4) alternate below.)

        Complexity: O(n^3) time with hash, O(U) space.
        """
        n = len(nums)
        ans = 0
        # freq of values seen as potential 'd' from the right while expanding
        freq = Counter()
        # iterate k from right; maintain freq of nums[l] for l>k
        for c in range(n - 1, -1, -1):
            for b in range(c - 1, -1, -1):
                for a in range(b - 1, -1, -1):
                    ans += freq[nums[a] + nums[b] + nums[c]]
            freq[nums[c]] += 1
        return ans

    def countQuadruplets_brute(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate O(n^4) clarity brute force over all index tuples.

        Algorithm:
        - Nested i<j<k<l; count nums[i]+nums[j]+nums[k]==nums[l].

        Complexity: O(n^4) time, O(1) space.
        """
        n = len(nums)
        ans = 0
        for i in range(n):
            for j in range(i + 1, n):
                for k in range(j + 1, n):
                    for l in range(k + 1, n):
                        if nums[i] + nums[j] + nums[k] == nums[l]:
                            ans += 1
        return ans
# @lc code=end

