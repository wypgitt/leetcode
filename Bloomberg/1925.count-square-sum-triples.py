#
# @lc app=leetcode id=1925 lang=python3
#
# [1925] Count Square Sum Triples
#
# https://leetcode.com/problems/count-square-sum-triples/description/
#
# algorithms
# Easy (77.16%)
# Likes:    747
# Dislikes: 65
# Total Accepted:    192K
# Total Submissions: 249K
# Testcase Example:  "5"
#
# A square triple (a,b,c) is a triple where a, b, and c are integers and a^2 +
# b^2 = c^2.
#
# Given an integer n, return the number of square triples such that 1 <= a, b,
# c <= n.
#
# Example 1:
#
# Input: n = 5
# Output: 2
# Explanation: The square triples are (3,4,5) and (4,3,5).
#
# Example 2:
#
# Input: n = 10
# Output: 4
# Explanation: The square triples are (3,4,5), (4,3,5), (6,8,10), and (8,6,10).
#
# Constraints:
#
# 1 <= n <= 250
#

# @lc code=start
class Solution:
    def countTriples(self, n: int) -> int:
        """
        Interview explanation:
        Count triples (a,b,c) with a,b,c ∈ [1,n] and a^2+b^2=c^2.
        Enumerate a,b; check if c^2 is perfect square ≤ n^2.

        Algorithm:
        - Nested a,b; c2=a*a+b*b; c=isqrt(c2); if c*c==c2 and c<=n: count++.

        Complexity: O(n^2) time, O(1) space.
        """
        import math

        ans = 0
        for a in range(1, n + 1):
            for b in range(1, n + 1):
                c2 = a * a + b * b
                c = int(math.isqrt(c2))
                if c <= n and c * c == c2:
                    ans += 1
        return ans
# @lc code=end
