#
# @lc app=leetcode id=1707 lang=python3
#
# [1707] Maximum XOR With an Element From Array
#
# https://leetcode.com/problems/maximum-xor-with-an-element-from-array/description/
#
# algorithms
# Hard (59.12%)
# Likes:    1450
# Dislikes: 41
# Total Accepted:    51.5K
# Total Submissions: 87.2K
# Testcase Example:  "[0,1,2,3,4]"
#
# You are given an array nums consisting of non-negative integers. You are also
# given a queries array, where queries[i] = [x_i, m_i].
#
# The answer to the i^th query is the maximum bitwise XOR value of x_i and any
# element of nums that does not exceed m_i. In other words, the answer is
# max(nums[j] XOR x_i) for all j such that nums[j] <= m_i. If all elements in
# nums are larger than m_i, then the answer is -1.
#
# Return an integer array answer where answer.length == queries.length and
# answer[i] is the answer to the i^th query.
#
# Example 1:
#
# Input: nums = [0,1,2,3,4], queries = [[3,1],[1,3],[5,6]]
# Output: [3,3,7]
# Explanation:
# 1) 0 and 1 are the only two integers not greater than 1. 0 XOR 3 = 3 and 1
# XOR 3 = 2. The larger of the two is 3.
# 2) 1 XOR 2 = 3.
# 3) 5 XOR 2 = 7.
#
# Example 2:
#
# Input: nums = [5,2,4,6,6,3], queries = [[12,4],[8,1],[6,3]]
# Output: [15,-1,5]
#
# Constraints:
#
# 1 <= nums.length, queries.length <= 10^5
#
# queries[i].length == 2
#
# 0 <= nums[j], x_i, m_i <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def maximizeXor(self, nums: List[int], queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        For each query (x, m) find max nums[i]^x among nums[i]<=m. Offline: sort nums
        and queries by m; insert eligible nums into a binary trie; query max XOR.

        Algorithm:
        - Sort nums; sort queries by m keeping index.
        - Trie of bits (MSB first); insert nums <= m; query prefer opposite bit of x.

        Complexity: O((n+q) log A * 32) time, O(n*32) space.
        """
        nums = sorted(nums)
        qid = sorted(range(len(queries)), key=lambda i: queries[i][1])
        ans = [-1] * len(queries)

        class Node:
            __slots__ = ('ch',)
            def __init__(self):
                self.ch = [None, None]

        root = Node()
        ptr = 0

        def insert(v: int) -> None:
            node = root
            for b in range(31, -1, -1):
                bit = (v >> b) & 1
                if node.ch[bit] is None:
                    node.ch[bit] = Node()
                node = node.ch[bit]

        def query(x: int) -> int:
            node = root
            if node.ch[0] is None and node.ch[1] is None:
                return -1
            res = 0
            for b in range(31, -1, -1):
                bit = (x >> b) & 1
                want = 1 - bit
                if node.ch[want] is not None:
                    res |= 1 << b
                    node = node.ch[want]
                else:
                    node = node.ch[bit]
            return res

        for i in qid:
            x, m = queries[i]
            while ptr < len(nums) and nums[ptr] <= m:
                insert(nums[ptr])
                ptr += 1
            ans[i] = query(x)
        return ans
# @lc code=end
