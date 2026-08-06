#
# @lc app=leetcode id=1803 lang=python3
#
# [1803] Count Pairs With XOR in a Range
#
# https://leetcode.com/problems/count-pairs-with-xor-in-a-range/description/
#
# algorithms
# Hard (46.53%)
# Likes:    562
# Dislikes: 24
# Total Accepted:    12.8K
# Total Submissions: 27.6K
# Testcase Example:  "[1,4,2,7]"
#
# Given a (0-indexed) integer array nums and two integers low and high, return
# the number of nice pairs.
#
# A nice pair is a pair (i, j) where 0 <= i < j < nums.length and low <=
# (nums[i] XOR nums[j]) <= high.
#
# Example 1:
#
# Input: nums = [1,4,2,7], low = 2, high = 6
# Output: 6
# Explanation: All nice pairs (i, j) are as follows:
# - (0, 1): nums[0] XOR nums[1] = 5
# - (0, 2): nums[0] XOR nums[2] = 3
# - (0, 3): nums[0] XOR nums[3] = 6
# - (1, 2): nums[1] XOR nums[2] = 6
# - (1, 3): nums[1] XOR nums[3] = 3
# - (2, 3): nums[2] XOR nums[3] = 5
#
# Example 2:
#
# Input: nums = [9,8,4,2,1], low = 5, high = 14
# Output: 8
# Explanation: All nice pairs (i, j) are as follows:
# - (0, 2): nums[0] XOR nums[2] = 13
# - (0, 3): nums[0] XOR nums[3] = 11
# - (0, 4): nums[0] XOR nums[4] = 8
# - (1, 2): nums[1] XOR nums[2] = 12
# - (1, 3): nums[1] XOR nums[3] = 10
# - (1, 4): nums[1] XOR nums[4] = 9
# - (2, 3): nums[2] XOR nums[3] = 6
# - (2, 4): nums[2] XOR nums[4] = 5
#
# Constraints:
#
# 1 <= nums.length <= 2 * 10^4
#
# 1 <= nums[i] <= 2 * 10^4
#
# 1 <= low <= high <= 2 * 10^4
#

# @lc code=start
from typing import List


class Solution:
    def countPairs(self, nums: List[int], low: int, high: int) -> int:
        """
        Interview explanation:
        Count pairs with XOR in [low, high] = count(< high+1) - count(< low).
        Binary Trie of inserted numbers answers "how many have XOR < limit".

        Algorithm (binary Trie):
        - For each num (in order), query count with XOR < high+1 and < low, then insert.
        - Trie nodes store count; walk bits of limit, taking opposite bit when allowed.

        Complexity: O(n * 15) time/space (nums[i] < 2^15).
        """
        class Node:
            __slots__ = ("ch", "cnt")
            def __init__(self):
                self.ch = [None, None]
                self.cnt = 0

        root = Node()

        def insert(x: int) -> None:
            node = root
            for i in range(14, -1, -1):
                b = (x >> i) & 1
                if node.ch[b] is None:
                    node.ch[b] = Node()
                node = node.ch[b]
                node.cnt += 1

        def count_less(x: int, limit: int) -> int:
            node = root
            ans = 0
            for i in range(14, -1, -1):
                if node is None:
                    break
                xb = (x >> i) & 1
                lb = (limit >> i) & 1
                if lb:
                    # same-bit branch has XOR bit 0 < 1; take all
                    if node.ch[xb] is not None:
                        ans += node.ch[xb].cnt
                    node = node.ch[xb ^ 1]
                else:
                    node = node.ch[xb]
            return ans

        res = 0
        for num in nums:
            res += count_less(num, high + 1) - count_less(num, low)
            insert(num)
        return res
# @lc code=end
