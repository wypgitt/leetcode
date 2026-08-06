#
# @lc app=leetcode id=1652 lang=python3
#
# [1652] Defuse the Bomb
#
# https://leetcode.com/problems/defuse-the-bomb/description/
#
# algorithms
# Easy (79.41%)
# Likes:    1677
# Dislikes: 187
# Total Accepted:    237K
# Total Submissions: 298K
# Testcase Example:  "[5,7,1,4]"
#
# You have a bomb to defuse, and your time is running out! Your informer will
# provide you with a circular array code of length of n and a key k.
#
# To decrypt the code, you must replace every number. All the numbers are
# replaced simultaneously.
#
# If k > 0, replace the i^th number with the sum of the next k numbers.
#
# If k < 0, replace the i^th number with the sum of the previous -k numbers.
#
# If k == 0, replace the i^th number with 0.
#
# As code is circular, the next element of code[n-1] is code[0], and the
# previous element of code[0] is code[n-1].
#
# Given the circular array code and an integer key k, return the decrypted code
# to defuse the bomb!
#
# Example 1:
#
# Input: code = [5,7,1,4], k = 3
# Output: [12,10,16,13]
# Explanation: Each number is replaced by the sum of the next 3 numbers. The
# decrypted code is [7+1+4, 1+4+5, 4+5+7, 5+7+1]. Notice that the numbers wrap
# around.
#
# Example 2:
#
# Input: code = [1,2,3,4], k = 0
# Output: [0,0,0,0]
# Explanation: When k is zero, the numbers are replaced by 0.
#
# Example 3:
#
# Input: code = [2,4,9,3], k = -2
# Output: [12,5,6,13]
# Explanation: The decrypted code is [3+9, 2+3, 4+2, 9+4]. Notice that the
# numbers wrap around again. If k is negative, the sum is of the previous
# numbers.
#
# Constraints:
#
# n == code.length
#
# 1 <= n <= 100
#
# 1 <= code[i] <= 100
#
# -(n - 1) <= k <= n - 1
#

# @lc code=start
from typing import List


class Solution:
    def decrypt(self, code: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Circular array: each index becomes sum of next k (or previous -k) elements.
        Sliding window over doubled array avoids O(n*|k|) recompute.

        Algorithm (sliding window):
        - If k==0 return zeros.
        - Build window of length |k| starting at 1 (k>0) or n+k (k<0); slide n times.

        Complexity: O(n) time, O(n) space for answer.
        """
        n = len(code)
        if k == 0:
            return [0] * n
        ans = [0] * n
        extended = code + code
        if k > 0:
            window = sum(extended[1 : 1 + k])
            for i in range(n):
                ans[i] = window
                window += extended[i + 1 + k] - extended[i + 1]
        else:
            kk = -k
            window = sum(extended[n - kk : n])
            for i in range(n):
                ans[i] = window
                window += extended[i] - extended[n - kk + i]
        return ans

    def decrypt_bruteforce(self, code: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Classic alternate: for each i, sum the |k| neighbors with modular index.

        Algorithm:
        - For i in range(n): accumulate code[(i+j)%n] for j=1..k or j=-1..-kk.

        Complexity: O(n*|k|) time, O(n) space.
        """
        n = len(code)
        if k == 0:
            return [0] * n
        ans = [0] * n
        for i in range(n):
            s = 0
            if k > 0:
                for j in range(1, k + 1):
                    s += code[(i + j) % n]
            else:
                for j in range(1, -k + 1):
                    s += code[(i - j) % n]
            ans[i] = s
        return ans
# @lc code=end
