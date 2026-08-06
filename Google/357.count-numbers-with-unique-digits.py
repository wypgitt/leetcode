#
# @lc app=leetcode id=357 lang=python3
#
# [357] Count Numbers with Unique Digits
#
# https://leetcode.com/problems/count-numbers-with-unique-digits/description/
#
# algorithms
# Medium (56.03%)
# Likes:    1742
# Dislikes: 1528
# Total Accepted:    195K
# Total Submissions: 349K
# Testcase Example:  "2"
#
# Given an integer n, return the count of all numbers with unique digits, x,
# where 0 <= x < 10^n.
#
# Example 1:
#
# Input: n = 2
# Output: 91
# Explanation: The answer should be the total numbers in the range of 0 ≤ x <
# 100, excluding 11,22,33,44,55,66,77,88,99
#
# Example 2:
#
# Input: n = 0
# Output: 1
#
# Constraints:
#
# 0 <= n <= 8
#

# @lc code=start
class Solution:
    def countNumbersWithUniqueDigits(self, n: int) -> int:
        """
        Interview explanation:
        Count n-digit numbers with unique digits via permutations:
        f(1)=10; for length k>=2: 9 * P(9, k-1) = 9*9*8*...*(10-k+1).
        Answer is sum f(1)..f(n) (including 0 for n>=1 via f(1)).

        Algorithm:
        - If n == 0 return 1.
        - ans = 10; cur = 9; available = 9; for i in 2..n: cur *= available;
          ans += cur; available -= 1.

        Complexity: O(n) time, O(1) space (n <= 8 typically).
        """
        if n == 0:
            return 1
        ans = 10
        cur = 9
        available = 9
        for _ in range(2, n + 1):
            cur *= available
            ans += cur
            available -= 1
        return ans
# @lc code=end
