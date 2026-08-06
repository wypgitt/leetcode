#
# @lc app=leetcode id=2935 lang=python3
#
# [2935] Maximum Strong Pair XOR II
#
# https://leetcode.com/problems/maximum-strong-pair-xor-ii/description/
#
# algorithms
# Hard (32.74%)
# Likes:    213
# Dislikes: 2
# Total Accepted:    9.4K
# Total Submissions: 28.6K
# Testcase Example:  "[1,2,3,4,5]"
#
#
# You are given a 0-indexed integer array nums. A pair of integers x and y
# is called a strong pair if it satisfies the condition:
#
# |x - y| <= min(x, y)
#
# You need to select two integers from nums such that they form a strong
# pair and their bitwise XOR is the maximum among all strong pairs in the
# array.
#
# Return the maximum XOR value out of all possible strong pairs in the
# array nums.
#
# Note that you can pick the same integer twice to form a pair.
#
# Example 1:
#
# Input: nums = [1,2,3,4,5]
# Output: 7
# Explanation: There are 11 strong pairs in the array nums: (1, 1), (1,
# 2), (2, 2), (2, 3), (2, 4), (3, 3), (3, 4), (3, 5), (4, 4), (4, 5) and
# (5, 5).
# The maximum XOR possible from these pairs is 3 XOR 4 = 7.
#
# Example 2:
#
# Input: nums = [10,100]
# Output: 0
# Explanation: There are 2 strong pairs in the array nums: (10, 10) and
# (100, 100).
# The maximum XOR possible from these pairs is 10 XOR 10 = 0 since the
# pair (100, 100) also gives 100 XOR 100 = 0.
#
# Example 3:
#
# Input: nums = [500,520,2500,3000]
# Output: 1020
# Explanation: There are 6 strong pairs in the array nums: (500, 500),
# (500, 520), (520, 520), (2500, 2500), (2500, 3000) and (3000, 3000).
# The maximum XOR possible from these pairs is 500 XOR 520 = 1020 since
# the only other non-zero XOR value is 2500 XOR 3000 = 636.
#
# Constraints:
#
# 1 <= nums.length <= 5 * 10^4
#
# 1 <= nums[i] <= 2^20 - 1
#

# @lc code=start

class Solution:
    def maximumStrongPairXor(self, nums: list[int]) -> int:
        """
        Interview explanation:
        Same strong-pair XOR as I, but n <= 5e4. After sorting, for each right
        value y a valid left x satisfies y/2 <= x <= y. Maximize XOR in window.

        Algorithm:
        - Sort; sliding window + binary trie (insert/erase/query max XOR).

        Complexity: O(n log A) time, O(n log A) space.
        """
        nums = sorted(nums)
        # trie: node -> [zero, one, count]
        trie = [[0, 0, 0]]

        def add(x: int, delta: int) -> None:
            node = 0
            trie[node][2] += delta
            for b in range(19, -1, -1):
                bit = (x >> b) & 1
                if trie[node][bit] == 0:
                    trie[node][bit] = len(trie)
                    trie.append([0, 0, 0])
                node = trie[node][bit]
                trie[node][2] += delta

        def max_xor(x: int) -> int:
            if trie[0][2] == 0:
                return 0
            node, res = 0, 0
            for b in range(19, -1, -1):
                bit = (x >> b) & 1
                want = 1 - bit
                nxt = trie[node][want]
                if nxt and trie[nxt][2] > 0:
                    res |= 1 << b
                    node = nxt
                else:
                    node = trie[node][bit]
            return res

        ans = 0
        left = 0
        for y in nums:
            add(y, 1)
            while nums[left] * 2 < y:
                add(nums[left], -1)
                left += 1
            ans = max(ans, max_xor(y))
        return ans
# @lc code=end

