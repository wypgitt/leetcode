#
# @lc app=leetcode id=1718 lang=python3
#
# [1718] Construct the Lexicographically Largest Valid Sequence
#
# https://leetcode.com/problems/construct-the-lexicographically-largest-valid-sequence/description/
#
# algorithms
# Medium (72.64%)
# Likes:    1165
# Dislikes: 183
# Total Accepted:    114K
# Total Submissions: 157K
# Testcase Example:  "3"
#
# Given an integer n, find a sequence with elements in the range [1, n] that
# satisfies all of the following:
#
# The integer 1 occurs once in the sequence.
#
# Each integer between 2 and n occurs twice in the sequence.
#
# For every integer i between 2 and n, the distance between the two occurrences
# of i is exactly i.
#
# The distance between two numbers on the sequence, a[i] and a[j], is the
# absolute difference of their indices, |j - i|.
#
# Return the lexicographically largest sequence. It is guaranteed that under
# the given constraints, there is always a solution.
#
# A sequence a is lexicographically larger than a sequence b (of the same
# length) if in the first position where a and b differ, sequence a has a
# number greater than the corresponding number in b. For example, [0,1,9,0] is
# lexicographically larger than [0,1,5,6] because the first position they
# differ is at the third number, and 9 is greater than 5.
#
# Example 1:
#
# Input: n = 3
# Output: [3,1,2,3,2]
# Explanation: [2,3,2,1,3] is also a valid sequence, but [3,1,2,3,2] is the
# lexicographically largest valid sequence.
#
# Example 2:
#
# Input: n = 5
# Output: [5,3,1,4,3,5,2,4,2]
#
# Constraints:
#
# 1 <= n <= 20
#

# @lc code=start
from typing import List


class Solution:
    def constructDistancedSequence(self, n: int) -> List[int]:
        """
        Interview explanation:
        Build lex-largest sequence of length 2n-1 where 1 appears once and each
        k in 2..n appears twice at distance k. Backtrack placing largest numbers first.

        Algorithm:
        - seq array of size 2n-1; used set.
        - At empty index i, try place n..1; for k>1 also place at i+k if free.
        - Return first success (lex-largest due to trying large first).

        Complexity: O((2n)! / ...) search pruned; n<=20 so feasible. O(n) space.
        """
        size = 2 * n - 1
        seq = [0] * size
        used = [False] * (n + 1)

        def dfs(i: int) -> bool:
            if i == size:
                return True
            if seq[i]:
                return dfs(i + 1)
            for num in range(n, 0, -1):
                if used[num]:
                    continue
                if num == 1:
                    seq[i] = 1
                    used[1] = True
                    if dfs(i + 1):
                        return True
                    seq[i] = 0
                    used[1] = False
                else:
                    j = i + num
                    if j < size and seq[j] == 0:
                        seq[i] = seq[j] = num
                        used[num] = True
                        if dfs(i + 1):
                            return True
                        seq[i] = seq[j] = 0
                        used[num] = False
            return False

        dfs(0)
        return seq
# @lc code=end
