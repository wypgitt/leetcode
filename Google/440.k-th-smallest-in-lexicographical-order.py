#
# @lc app=leetcode id=440 lang=python3
#
# [440] K-th Smallest in Lexicographical Order
#
# https://leetcode.com/problems/k-th-smallest-in-lexicographical-order/description/
#
# algorithms
# Hard (46.47%)
# Likes:    1656
# Dislikes: 148
# Total Accepted:    172K
# Total Submissions: 370K
# Testcase Example:  "13"
#
# Given two integers n and k, return the k^th lexicographically smallest
# integer in the range [1, n].
#
# Example 1:
#
# Input: n = 13, k = 2
# Output: 10
# Explanation: The lexicographical order is [1, 10, 11, 12, 13, 2, 3, 4, 5, 6,
# 7, 8, 9], so the second smallest number is 10.
#
# Example 2:
#
# Input: n = 1, k = 1
# Output: 1
#
# Constraints:
#
# 1 <= k <= n <= 10^9
#

# @lc code=start

class Solution:
    def findKthNumber(self, n: int, k: int) -> int:
        """
        Interview explanation:
        Denary trie / lexicographic skip: at prefix `cur`, count how many numbers
        ≤ n lie in the subtree. If count < k, skip to cur+1; else descend to cur*10.

        Algorithm:
        - Start cur=1, k-=1 (1 is first).
        - While k>0: steps = count(cur, cur+1); if steps<=k: k-=steps; cur+=1;
          else: k-=1; cur*=10.
        - count(a,b): numbers in [a,b) prefix range capped by n.

        Complexity: O(log^2 n) time, O(1) space.
        """
        def count_steps(a: int, b: int) -> int:
            steps = 0
            while a <= n:
                steps += min(n + 1, b) - a
                a *= 10
                b *= 10
            return steps

        cur = 1
        k -= 1
        while k > 0:
            steps = count_steps(cur, cur + 1)
            if steps <= k:
                k -= steps
                cur += 1
            else:
                k -= 1
                cur *= 10
        return cur
# @lc code=end
