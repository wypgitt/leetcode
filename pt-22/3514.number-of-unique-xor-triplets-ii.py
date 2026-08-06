#
# @lc app=leetcode id=3514 lang=python3
#
# [3514] Number of Unique XOR Triplets II
#
# https://leetcode.com/problems/number-of-unique-xor-triplets-ii/description/
#
# algorithms
# Medium (52.89%)
# Likes:    217
# Dislikes: 25
# Total Accepted:    96.3K
# Total Submissions: 182.1K
# Testcase Example:  "[1,3]"
#
#
# You are given an integer array nums.
#
# A XOR triplet is defined as the XOR of three elements nums[i] XOR
# nums[j] XOR nums[k] where i <= j <= k.
#
# Return the number of unique XOR triplet values from all possible
# triplets (i, j, k).
#
# Example 1:
#
# Input: nums = [1,3]
#
# Output: 2
#
# Explanation:
#
# The possible XOR triplet values are:
#
# (0, 0, 0) → 1 XOR 1 XOR 1 = 1
#
# (0, 0, 1) → 1 XOR 1 XOR 3 = 3
#
# (0, 1, 1) → 1 XOR 3 XOR 3 = 1
#
# (1, 1, 1) → 3 XOR 3 XOR 3 = 3
#
# The unique XOR values are {1, 3}. Thus, the output is 2.
#
# Example 2:
#
# Input: nums = [6,7,8,9]
#
# Output: 4
#
# Explanation:
#
# The possible XOR triplet values are {6, 7, 8, 9}. Thus, the output is 4.
#
# Constraints:
#
# 1 <= nums.length <= 1500
#
# 1 <= nums[i] <= 1500
#

# @lc code=start
from typing import List


class Solution:
    def uniqueXorTriplets(self, nums: List[int]) -> int:
        """
        Interview explanation:
        With i <= j <= k, any three values from the array (same index reusable)
        can form an XOR. Mark all pairwise XORs, then XOR each with every array
        value; count distinct results.

        Algorithm:
        - Boolean array over [0, 2*max]; mark a^b for all a,b in nums.
        - Mark ab^c for each marked ab and c in nums; sum marks.

        Complexity: O(n^2 + M n) time, O(M) space (M ~ 2 max(nums)).
        """
        mx = max(nums) << 1
        st = [False] * mx
        for a in nums:
            for b in nums:
                st[a ^ b] = True
        s = [0] * mx
        for ab in range(mx):
            if st[ab]:
                for c in nums:
                    s[ab ^ c] = 1
        return sum(s)
# @lc code=end
