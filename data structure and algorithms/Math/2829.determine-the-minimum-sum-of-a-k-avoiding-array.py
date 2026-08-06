#
# @lc app=leetcode id=2829 lang=python3
#
# [2829] Determine the Minimum Sum of a k-avoiding Array
#
# https://leetcode.com/problems/determine-the-minimum-sum-of-a-k-avoiding-array/description/
#
# algorithms
# Medium (61.13%)
# Likes:    354
# Dislikes: 13
# Total Accepted:    42K
# Total Submissions: 68.8K
# Testcase Example:  "5\n4"
#
#
# You are given two integers, n and k.
#
# An array of distinct positive integers is called a k-avoiding array if
# there does not exist any pair of distinct elements that sum to k.
#
# Return the minimum possible sum of a k-avoiding array of length n.
#
# Example 1:
#
# Input: n = 5, k = 4
# Output: 18
# Explanation: Consider the k-avoiding array [1,2,4,5,6], which has a sum
# of 18.
# It can be proven that there is no k-avoiding array with a sum less than
# 18.
#
# Example 2:
#
# Input: n = 2, k = 6
# Output: 3
# Explanation: We can construct the array [1,2], which has a sum of 3.
# It can be proven that there is no k-avoiding array with a sum less than
# 3.
#
# Constraints:
#
# 1 <= n, k <= 50
#

# @lc code=start
class Solution:
    def minimumSum(self, n: int, k: int) -> int:
        """
        Interview explanation:
        Build a length-n set of distinct positives with no two summing to k,
        minimizing the sum. Prefer smallest unused positives.

        Algorithm:
        - Greedily take 1, 2, ... skipping x if (k - x) is already chosen.
        - Equivalent math: take 1..min(n, ceil(k/2)-1), then continue from k.

        Complexity: O(n) time, O(n) space.
        """
        chosen = set()
        x = 1
        total = 0
        while len(chosen) < n:
            if (k - x) not in chosen:
                chosen.add(x)
                total += x
            x += 1
        return total

    def minimumSum_math(self, n: int, k: int) -> int:
        """
        Interview explanation:
        Closed-form greedy intervals: [1, k//2] then [k, ...] (k/2 is safe once
        when k is even; complements of 1..k//2 start at >= k).

        Algorithm:
        - Let m = k // 2. If n <= m, sum is triangular(n).
        - Else sum 1..m plus n-m consecutive integers starting at k.

        Complexity: O(1) time, O(1) space.
        """
        m = k // 2
        if n <= m:
            return n * (n + 1) // 2
        first = m * (m + 1) // 2
        rem = n - m
        return first + rem * (2 * k + rem - 1) // 2
# @lc code=end
