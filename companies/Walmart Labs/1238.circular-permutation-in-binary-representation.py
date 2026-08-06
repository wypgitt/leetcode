#
# @lc app=leetcode id=1238 lang=python3
#
# [1238] Circular Permutation in Binary Representation
#
# https://leetcode.com/problems/circular-permutation-in-binary-representation/description/
#
# algorithms
# Medium (72.96%)
# Likes:    445
# Dislikes: 195
# Total Accepted:    25.8K
# Total Submissions: 35.4K
# Testcase Example:  "2"
#
# Given 2 integers n and start. Your task is return any permutation p of
# (0,1,2.....,2^n -1) such that :
#
# p[0] = start
#
# p[i] and p[i+1] differ by only one bit in their binary representation.
#
# p[0] and p[2^n -1] must also differ by only one bit in their binary
# representation.
#
# Example 1:
#
# Input: n = 2, start = 3
# Output: [3,2,0,1]
# Explanation: The binary representation of the permutation is (11,10,00,01).
# All the adjacent element differ by one bit. Another valid permutation is
# [3,1,0,2]
#
# Example 2:
#
# Input: n = 3, start = 2
# Output: [2,6,7,5,4,0,1,3]
# Explanation: The binary representation of the permutation is
# (010,110,111,101,100,000,001,011).
#
# Constraints:
#
# 1 <= n <= 16
#
# 0 <= start < 2 ^ n
#


# @lc code=start
from typing import List

class Solution:
    def circularPermutation(self, n: int, start: int) -> List[int]:
        """
        Interview explanation:
        Generate circular Gray code of n bits starting at `start`. Standard
        Gray code i^(i>>1) then XOR with start so sequence begins at start.

        Algorithm:
        - return [start ^ (i ^ (i >> 1)) for i in range(1<<n)]

        Complexity: O(2^n) time/space.
        """
        return [start ^ (i ^ (i >> 1)) for i in range(1 << n)]

    def circularPermutation_dfs(self, n: int, start: int) -> List[int]:
        """
        Interview explanation:
        Alternate: DFS/backtrack flipping one bit at a time until 2^n numbers,
        start from `start`.

        Algorithm:
        - visited bitset; append start; recurse flip each bit; backtrack

        Complexity: O(n * 2^n) time.
        """
        N = 1 << n
        ans = [start]
        seen = {start}

        def dfs(cur: int) -> bool:
            if len(ans) == N:
                return True
            for b in range(n):
                nxt = cur ^ (1 << b)
                if nxt not in seen:
                    seen.add(nxt)
                    ans.append(nxt)
                    if dfs(nxt):
                        return True
                    ans.pop()
                    seen.remove(nxt)
            return False

        dfs(start)
        return ans
# @lc code=end
