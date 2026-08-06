#
# @lc app=leetcode id=3632 lang=python3
#
# [3632] Subarrays with XOR at Least K
#
# https://leetcode.com/problems/subarrays-with-xor-at-least-k/description/
#
# algorithms
# Hard (45.13%)
# Likes:    4
# Dislikes: 2
# Total Accepted:    324
# Total Submissions: 718
# Testcase Example:  "[3,1,2,3]\n2"
#
#
# Given an array of positive integers nums of length n and a non‑negative
# integer k.
#
# Return the number of contiguous subarrays whose bitwise XOR of all
# elements is greater than or equal to k.
#
# Example 1:
#
# Input: nums = [3,1,2,3], k = 2
#
# Output: 6
#
# Explanation:
#
# The valid subarrays with XOR >= 2 are [3] at index 0, [3, 1] at indices
# 0 - 1, [3, 1, 2, 3] at indices 0 - 3, [1, 2] at indices 1 - 2, [2] at
# index 2, and [3] at index 3; there are 6 in total.
#
# Example 2:
#
# Input: nums = [0,0,0], k = 0
#
# Output: 6
#
# Explanation:
#
# Every contiguous subarray yields XOR = 0, which meets k = 0. There are 6
# such subarrays in total.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 10^9
#
# 0 <= k <= 10^9
#

# @lc code=start

from typing import List


class Solution:
    def countXorSubarrays(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Count subarrays with XOR >= k. Maintain a binary trie of prefix XORs;
        for each new prefix P, count prior prefixes Q with P^Q >= k.

        Algorithm:
        - Insert 0 into the trie.
        - For each x: P ^= x; ans += trie.count_gte(P, k); trie.insert(P).
        - Trie walk MSB->LSB: when k-bit is 0, add the branch with XOR-bit 1
          and continue on XOR-bit 0; when k-bit is 1, only continue on XOR-bit 1;
          equals at the leaf also count.

        Complexity: O(n log A) time and space.
        """
        class Trie:
            def __init__(self, bits: int):
                self.bits = bits
                self.nodes = [[-1, -1, 0]]

            def add(self, num: int) -> None:
                curr = 0
                self.nodes[curr][2] += 1
                for i in range(self.bits - 1, -1, -1):
                    b = (num >> i) & 1
                    if self.nodes[curr][b] == -1:
                        self.nodes[curr][b] = len(self.nodes)
                        self.nodes.append([-1, -1, 0])
                    curr = self.nodes[curr][b]
                    self.nodes[curr][2] += 1

            def count_gte(self, prefix: int, threshold: int) -> int:
                curr = 0
                ans = 0
                for i in range(self.bits - 1, -1, -1):
                    if curr == -1:
                        return ans
                    kb = (threshold >> i) & 1
                    pb = (prefix >> i) & 1
                    if kb == 0:
                        other = self.nodes[curr][1 - pb]
                        if other != -1:
                            ans += self.nodes[other][2]
                        curr = self.nodes[curr][pb]
                    else:
                        curr = self.nodes[curr][1 - pb]
                if curr != -1:
                    ans += self.nodes[curr][2]
                return ans

        bits = max(max(nums), k, 1).bit_length()
        trie = Trie(bits)
        trie.add(0)
        ans = prefix = 0
        for x in nums:
            prefix ^= x
            ans += trie.count_gte(prefix, k)
            trie.add(prefix)
        return ans
# @lc code=end

