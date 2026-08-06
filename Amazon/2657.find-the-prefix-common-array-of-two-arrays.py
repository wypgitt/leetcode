#
# @lc app=leetcode id=2657 lang=python3
#
# [2657] Find the Prefix Common Array of Two Arrays
#
# https://leetcode.com/problems/find-the-prefix-common-array-of-two-arrays/description/
#
# algorithms
# Medium (88.29%)
# Likes:    1392
# Dislikes: 79
# Total Accepted:    362.6K
# Total Submissions: 410.6K
# Testcase Example:  "[1,3,2,4]\n[3,1,2,4]"
#
# You are given two 0-indexed integer permutations A and B of length n.
#
# A prefix common array of A and B is an array C such that C[i] is equal to the
# count of numbers that are present at or before the index i in both A and B.
#
# Return the prefix common array of A and B.
#
# A sequence of n integers is called a permutation if it contains all integers
# from 1 to n exactly once.
#
#
#
# Example 1:
#
# Input: A = [1,3,2,4], B = [3,1,2,4]
# Output: [0,2,3,4]
# Explanation: At i = 0: no number is common, so C[0] = 0.
# At i = 1: 1 and 3 are common in A and B, so C[1] = 2.
# At i = 2: 1, 2, and 3 are common in A and B, so C[2] = 3.
# At i = 3: 1, 2, 3, and 4 are common in A and B, so C[3] = 4.
#
# Example 2:
#
# Input: A = [2,3,1], B = [3,1,2]
# Output: [0,1,3]
# Explanation: At i = 0: no number is common, so C[0] = 0.
# At i = 1: only 3 is common in A and B, so C[1] = 1.
# At i = 2: 1, 2, and 3 are common in A and B, so C[2] = 3.
#
#
#
# Constraints:
#
#
# 1 <= A.length == B.length == n <= 50
#
#
# 1 <= A[i], B[i] <= n
#
#
# It is guaranteed that A and B are both a permutation of n integers.
#

# @lc code=start

from typing import List


class Solution:
    def findThePrefixCommonArray(self, A: List[int], B: List[int]) -> List[int]:
        """
        Interview explanation:
        A, B permutations of 1..n. C[i] = count of values in both prefixes A[:i+1] and B[:i+1].

        Algorithm:
        - Count occurrences across both prefixes; when a value hits 2 it becomes common.

        Complexity: O(n) time, O(n) space.
        """
        n = len(A)
        cnt = [0] * (n + 1)
        ans = [0] * n
        common = 0
        for i in range(n):
            cnt[A[i]] += 1
            if cnt[A[i]] == 2:
                common += 1
            cnt[B[i]] += 1
            if cnt[B[i]] == 2:
                common += 1
            ans[i] = common
        return ans

    def findThePrefixCommonArray_set(self, A: List[int], B: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate sets: track seen prefixes; common size is intersection length.

        Algorithm:
        - Insert A[i], B[i]; append |sa ∩ sb|.

        Complexity: O(n^2) time naive, O(n) space.
        """
        sa: set[int] = set()
        sb: set[int] = set()
        ans: List[int] = []
        for a, b in zip(A, B):
            sa.add(a)
            sb.add(b)
            ans.append(len(sa & sb))
        return ans
# @lc code=end
