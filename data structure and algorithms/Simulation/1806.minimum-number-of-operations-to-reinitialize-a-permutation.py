#
# @lc app=leetcode id=1806 lang=python3
#
# [1806] Minimum Number of Operations to Reinitialize a Permutation
#
# https://leetcode.com/problems/minimum-number-of-operations-to-reinitialize-a-permutation/description/
#
# algorithms
# Medium (72.67%)
# Likes:    329
# Dislikes: 177
# Total Accepted:    24.0K
# Total Submissions: 33.0K
# Testcase Example:  "2"
#
# You are given an even integer n. You initially have a permutation perm of
# size n where perm[i] == i (0-indexed).
#
# In one operation, you will create a new array arr, and for each i:
#
# If i % 2 == 0, then arr[i] = perm[i / 2].
#
# If i % 2 == 1, then arr[i] = perm[n / 2 + (i - 1) / 2].
#
# You will then assign arr to perm.
#
# Return the minimum non-zero number of operations you need to perform on perm
# to return the permutation to its initial value.
#
# Example 1:
#
# Input: n = 2
# Output: 1
# Explanation: perm = [0,1] initially.
# After the 1^st operation, perm = [0,1]
# So it takes only 1 operation.
#
# Example 2:
#
# Input: n = 4
# Output: 2
# Explanation: perm = [0,1,2,3] initially.
# After the 1^st operation, perm = [0,2,1,3]
# After the 2^nd operation, perm = [0,1,2,3]
# So it takes only 2 operations.
#
# Example 3:
#
# Input: n = 6
# Output: 4
#
# Constraints:
#
# 2 <= n <= 1000
#
# n is even.
#

# @lc code=start
class Solution:
    def reinitializePermutation(self, n: int) -> int:
        """
        Interview explanation:
        Permutation: even i -> i/2; odd -> n/2 + (i-1)/2. Find order of ops to
        identity. Track image of index 1 under repeated map until back to 1.

        Algorithm (simulate index 1):
        - Start at 1; while != 1 after steps: if even i//=2 else i = n//2+(i-1)//2.
        - Answer is steps (for n=2 answer 1).

        Complexity: O(n) time, O(1) space.
        """
        if n == 2:
            return 1
        i, steps = 1, 0
        while True:
            if i % 2 == 0:
                i //= 2
            else:
                i = n // 2 + (i - 1) // 2
            steps += 1
            if i == 1:
                return steps

    def reinitializePermutation_full(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: simulate full array until it matches [0..n-1].

        Algorithm (full simulation):
        - Apply perm until arr == identity; count ops.

        Complexity: O(n * order) time, O(n) space.
        """
        arr = list(range(n))
        target = list(range(n))
        steps = 0
        while True:
            arr = [arr[i // 2] if i % 2 == 0 else arr[n // 2 + (i - 1) // 2] for i in range(n)]
            steps += 1
            if arr == target:
                return steps
# @lc code=end
