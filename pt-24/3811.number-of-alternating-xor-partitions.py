#
# @lc app=leetcode id=3811 lang=python3
#
# [3811] Number of Alternating XOR Partitions
#
# https://leetcode.com/problems/number-of-alternating-xor-partitions/description/
#
# algorithms
# Medium (27.37%)
# Likes:    97
# Dislikes: 9
# Total Accepted:    9.2K
# Total Submissions: 33.5K
# Testcase Example:  "[2,3,1,4]\n1\n5"
#
#
# You are given an integer array nums and two distinct integers target1
# and target2.
#
# A partition of nums splits it into one or more contiguous, non-empty
# blocks that cover the entire array without overlap.
#
# A partition is valid if the bitwise XOR of elements in its blocks
# alternates between target1 and target2, starting with target1.
#
# Formally, for blocks b1, b2, …:
#
# XOR(b1) = target1
#
# XOR(b2) = target2 (if it exists)
#
# XOR(b3) = target1, and so on.
#
# Return the number of valid partitions of nums, modulo 10^9 + 7.
#
# Note: A single block is valid if its XOR equals target1.
#
# Example 1:
#
# Input: nums = [2,3,1,4], target1 = 1, target2 = 5
#
# Output: 1
#
# Explanation:​​​​​​​
#
# The XOR of [2, 3] is 1, which matches target1.
#
# The XOR of the remaining block [1, 4] is 5, which matches target2.
#
# This is the only valid alternating partition, so the answer is 1.
#
# Example 2:
#
# Input: nums = [1,0,0], target1 = 1, target2 = 0
#
# Output: 3
#
# Explanation:
#
# ​​​​​​​The XOR of [1, 0, 0] is 1, which matches target1.
#
# The XOR of [1] and [0, 0] are 1 and 0, matching target1 and target2.
#
# The XOR of [1, 0] and [0] are 1 and 0, matching target1 and target2.
#
# Thus, the answer is 3.​​​​​​​
#
# Example 3:
#
# Input: nums = [7], target1 = 1, target2 = 7
#
# Output: 0
#
# Explanation:
#
# The XOR of [7] is 7, which does not match target1, so no valid partition
# exists.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 0 <= nums[i], target1, target2 <= 10^5
#
# target1 != target2
#

# @lc code=start

from collections import defaultdict
from typing import List


class Solution:
    def alternatingXOR(
        self, nums: List[int], target1: int, target2: int
    ) -> int:
        """
        Interview explanation:
        Count ways to cut nums into blocks whose XORs alternate target1,
        target2, target1, ... . Use prefix XOR + DP maps of ways ending on
        each target.

        Algorithm:
        - cnt1[p] / cnt2[p]: ways to partition a prefix with XOR p ending on
          target1 / target2. Seed cnt2[0] = 1 (empty).
        - For prefix XOR pre, ways to close a target1 block: cnt2[pre^target1];
          for target2: cnt1[pre^target2]. Accumulate into maps; answer is the
          total ways after the full array.

        Complexity: O(n) time, O(n) space.
        """
        MOD = 10**9 + 7
        cnt1: dict[int, int] = defaultdict(int)
        cnt2: dict[int, int] = defaultdict(int)
        cnt2[0] = 1
        ans = pre = 0
        for x in nums:
            pre ^= x
            a = cnt2[pre ^ target1]
            b = cnt1[pre ^ target2]
            ans = (a + b) % MOD
            cnt1[pre] = (cnt1[pre] + a) % MOD
            cnt2[pre] = (cnt2[pre] + b) % MOD
        return ans
# @lc code=end
