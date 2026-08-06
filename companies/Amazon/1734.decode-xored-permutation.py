#
# @lc app=leetcode id=1734 lang=python3
#
# [1734] Decode XORed Permutation
#
# https://leetcode.com/problems/decode-xored-permutation/description/
#
# algorithms
# Medium (67.17%)
# Likes:    811
# Dislikes: 35
# Total Accepted:    21.3K
# Total Submissions: 31.7K
# Testcase Example:  "[3,1]"
#
# There is an integer array perm that is a permutation of the first n positive
# integers, where n is always odd.
#
# It was encoded into another integer array encoded of length n - 1, such that
# encoded[i] = perm[i] XOR perm[i + 1]. For example, if perm = [1,3,2], then
# encoded = [2,1].
#
# Given the encoded array, return the original array perm. It is guaranteed
# that the answer exists and is unique.
#
# Example 1:
#
# Input: encoded = [3,1]
# Output: [1,2,3]
# Explanation: If perm = [1,2,3], then encoded = [1 XOR 2,2 XOR 3] = [3,1]
#
# Example 2:
#
# Input: encoded = [6,5,4,6]
# Output: [2,4,1,5,3]
#
# Constraints:
#
# 3 <= n < 10^5
#
# n is odd.
#
# encoded.length == n - 1
#

# @lc code=start
from typing import List


class Solution:
    def decode(self, encoded: List[int]) -> List[int]:
        """
        Interview explanation:
        encoded[i] = perm[i] XOR perm[i+1] for a permutation of 1..n (n odd).
        XOR of 1..n and XOR of encoded at odd indices recovers perm[0], then
        decode sequentially.

        Algorithm:
        - total = XOR of 1..n
        - odd = encoded[1] XOR encoded[3] XOR ...
        - first = total XOR odd; then arr[i+1] = arr[i] XOR encoded[i]

        Complexity: O(n) time, O(n) space.
        """
        n = len(encoded) + 1
        total = 0
        for i in range(1, n + 1):
            total ^= i
        odd = 0
        for i in range(1, len(encoded), 2):
            odd ^= encoded[i]
        first = total ^ odd
        perm = [first]
        for e in encoded:
            perm.append(perm[-1] ^ e)
        return perm
# @lc code=end
