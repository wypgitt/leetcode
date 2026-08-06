#
# @lc app=leetcode id=421 lang=python3
#
# [421] Maximum XOR of Two Numbers in an Array
#
# https://leetcode.com/problems/maximum-xor-of-two-numbers-in-an-array/description/
#
# algorithms
# Medium (53.69%)
# Likes:    6004
# Dislikes: 424
# Total Accepted:    234K
# Total Submissions: 436K
# Testcase Example:  "[3,10,5,25,2,8]"
#
# Given an integer array nums, return the maximum result of nums[i] XOR
# nums[j], where 0 <= i <= j < n.
#
# Example 1:
#
# Input: nums = [3,10,5,25,2,8]
# Output: 28
# Explanation: The maximum result is 5 XOR 25 = 28.
#
# Example 2:
#
# Input: nums = [14,70,53,83,49,91,36,80,92,51,66,70]
# Output: 127
#
# Constraints:
#
# 1 <= nums.length <= 2 * 10^5
#
# 0 <= nums[i] <= 2^31 - 1
#

# @lc code=start

from typing import List


class Solution:
    def findMaximumXOR(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Binary trie of numbers (MSB first). For each num, greedily walk the
        opposite bit when possible to maximize XOR with any previously inserted
        number; insert all numbers first or insert as we go.

        Algorithm:
        - Build trie of all 32-bit prefixes.
        - For each num, query best XOR partner; track global max.

        Complexity: O(n * 32) time and space.
        """
        class Node:
            __slots__ = ("child",)

            def __init__(self):
                self.child = [None, None]

        root = Node()
        # insert
        for num in nums:
            node = root
            for b in range(31, -1, -1):
                bit = (num >> b) & 1
                if node.child[bit] is None:
                    node.child[bit] = Node()
                node = node.child[bit]

        best = 0
        for num in nums:
            node = root
            cur = 0
            for b in range(31, -1, -1):
                bit = (num >> b) & 1
                want = 1 - bit
                if node.child[want] is not None:
                    cur |= 1 << b
                    node = node.child[want]
                else:
                    node = node.child[bit]
            best = max(best, cur)
        return best

    def findMaximumXORPrefix(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate bit-by-bit with prefix sets: for each bit from high to low,
        assume it can be 1 in the answer; check if two prefixes exist that XOR
        to the candidate.

        Algorithm:
        - ans=0; for bit 31..0: candidate=ans|(1<<bit); if exists p,q in
          prefixes with p^q==candidate, set ans=candidate.

        Complexity: O(n * 32) time, O(n) space.
        """
        ans = 0
        mask = 0
        for b in range(31, -1, -1):
            mask |= 1 << b
            prefixes = {num & mask for num in nums}
            candidate = ans | (1 << b)
            if any((p ^ candidate) in prefixes for p in prefixes):
                ans = candidate
        return ans
# @lc code=end
