#
# @lc app=leetcode id=60 lang=python3
#
# [60] Permutation Sequence
#
# https://leetcode.com/problems/permutation-sequence/description/
#
# algorithms
# Hard (53.89%)
# Likes:    7344
# Dislikes: 511
# Total Accepted:    611K
# Total Submissions: 1.1M
# Testcase Example:  "3"
#
# The set [1, 2, 3, ..., n] contains a total of n! unique permutations.
#
# By listing and labeling all of the permutations in order, we get the
# following sequence for n = 3:
#
# "123"
#
# "132"
#
# "213"
#
# "231"
#
# "312"
#
# "321"
#
# Given n and k, return the k^th permutation sequence.
#
# Example 1:
#
# Input: n = 3, k = 3
# Output: "213"
#
# Example 2:
#
# Input: n = 4, k = 9
# Output: "2314"
#
# Example 3:
#
# Input: n = 3, k = 1
# Output: "123"
#
# Constraints:
#
# 1 <= n <= 9
#
# 1 <= k <= n!
#

# @lc code=start
class Solution:
    def getPermutation(self, n: int, k: int) -> str:
        """
        Interview explanation:
        The k-th permutation (1-indexed) maps directly to digits in the
        factorial number system. At each position, (n-1)! permutations share
        the same first digit among the remaining numbers.

        Algorithm:
        - Build remaining digits [1..n] and factorials.
        - Convert k to 0-index; for i from n down to 1:
          - index = k // (i-1)!; append remaining[index]; remove it;
            k %= (i-1)!.

        Complexity: O(n^2) time from list removals, O(n) space.
        """
        factorial = [1] * (n + 1)
        for i in range(1, n + 1):
            factorial[i] = factorial[i - 1] * i

        remaining = [str(i) for i in range(1, n + 1)]
        k -= 1
        ans = []

        for i in range(n, 0, -1):
            idx = k // factorial[i - 1]
            ans.append(remaining.pop(idx))
            k %= factorial[i - 1]

        return "".join(ans)
# @lc code=end
