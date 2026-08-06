#
# @lc app=leetcode id=873 lang=python3
#
# [873] Length of Longest Fibonacci Subsequence
#
# https://leetcode.com/problems/length-of-longest-fibonacci-subsequence/description/
#
# algorithms
# Medium (57.56%)
# Likes:    2703
# Dislikes: 110
# Total Accepted:    195K
# Total Submissions: 339K
# Testcase Example:  "[1,2,3,4,5,6,7,8]"
#
# A sequence x_1, x_2, ..., x_n is Fibonacci-like if:
#
# n >= 3
#
# x_i + x_i+1 == x_i+2 for all i + 2 <= n
#
# Given a strictly increasing array arr of positive integers forming a
# sequence, return the length of the longest Fibonacci-like subsequence of arr.
# If one does not exist, return 0.
#
# A subsequence is derived from another sequence arr by deleting any number of
# elements (including none) from arr, without changing the order of the
# remaining elements. For example, [3, 5, 8] is a subsequence of [3, 4, 5, 6,
# 7, 8].
#
# Example 1:
#
# Input: arr = [1,2,3,4,5,6,7,8]
# Output: 5
# Explanation: The longest subsequence that is fibonacci-like: [1,2,3,5,8].
#
# Example 2:
#
# Input: arr = [1,3,7,11,12,14,18]
# Output: 3
# Explanation: The longest subsequence that is fibonacci-like: [1,11,12],
# [3,11,14] or [7,11,18].
#
# Constraints:
#
# 3 <= arr.length <= 1000
#
# 1 <= arr[i] < arr[i + 1] <= 10^9
#

# @lc code=start
from typing import Dict, List, Tuple


class Solution:
    def lenLongestFibSubseq(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Strictly increasing arr. DP on pairs: dp[j][i] = longest Fib ending
        with arr[j],arr[i]. If arr[i]-arr[j] exists at k<j, extend.

        Algorithm (DP):
        - index map value->i. dp[(j,i)] = dp.get((k,j),2)+1 when arr[k]+arr[j]=arr[i].
        - Track max length; return 0 if <3.

        Complexity: O(n^2) time/space.
        """
        n = len(arr)
        idx = {v: i for i, v in enumerate(arr)}
        dp: Dict[Tuple[int, int], int] = {}
        ans = 0
        for i in range(n):
            for j in range(i):
                x = arr[i] - arr[j]
                k = idx.get(x)
                if k is not None and k < j:
                    dp[(j, i)] = dp.get((k, j), 2) + 1
                    ans = max(ans, dp[(j, i)])
                else:
                    dp[(j, i)] = 2
        return ans if ans >= 3 else 0

    def lenLongestFibSubseq_set(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Alternate: for each pair (arr[i],arr[j]) as Fib start, greedily extend
        while next sum exists in set.

        Algorithm:
        - S=set(arr). For all i<j: a,b=arr[i],arr[j]; length while a+b in S.

        Complexity: O(n^2 log M) time worst (extend), O(n) space.
        """
        S = set(arr)
        n = len(arr)
        ans = 0
        for i in range(n):
            for j in range(i + 1, n):
                a, b = arr[i], arr[j]
                length = 2
                while a + b in S:
                    a, b = b, a + b
                    length += 1
                if length >= 3:
                    ans = max(ans, length)
        return ans
# @lc code=end

