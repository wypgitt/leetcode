#
# @lc app=leetcode id=3704 lang=python3
#
# [3704] Count No-Zero Pairs That Sum to N
#
# https://leetcode.com/problems/count-no-zero-pairs-that-sum-to-n/description/
#
# algorithms
# Hard (15.25%)
# Likes:    61
# Dislikes: 3
# Total Accepted:    5.7K
# Total Submissions: 37.5K
# Testcase Example:  "2"
#
#
# A no-zero integer is a positive integer that does not contain the digit
# 0 in its decimal representation.
#
# Given an integer n, count the number of pairs (a, b) where:
#
# a and b are no-zero integers.
#
# a + b = n
#
# Return an integer denoting the number of such pairs.
#
# Example 1:
#
# Input: n = 2
#
# Output: 1
#
# Explanation:
#
# The only pair is (1, 1).
#
# Example 2:
#
# Input: n = 3
#
# Output: 2
#
# Explanation:
#
# The pairs are (1, 2) and (2, 1).
#
# Example 3:
#
# Input: n = 11
#
# Output: 8
#
# Explanation:
#
# The pairs are (2, 9), (3, 8), (4, 7), (5, 6), (6, 5), (7, 4), (8, 3),
# and (9, 2). Note that (1, 10) and (10, 1) do not satisfy the conditions
# because 10 contains 0 in its decimal representation.
#
# Constraints:
#
# 2 <= n <= 10^15
#

# @lc code=start

class Solution:
    def countNoZeroPairs(self, n: int) -> int:
        """
        Interview explanation:
        Count pairs of no-zero positives summing to n via digit DP over n's
        digits (LSD -> MSD), tracking carry and whether a/b are still open.

        Algorithm:
        - Digits of n reversed, plus a leading 0 to absorb final carry.
        - dp[carry][aliveA][aliveB]: ways for the processed suffix.
        - Alive side picks digits 1..9 (or may end with digit 0 after pos 0);
          finished side must pick 0.
        - Answer is dp[0][0][0] after the extra digit.

        Complexity: O(L * 9^2) time, O(1) space (L = digits of n).
        """
        digits = list(map(int, str(n)))[::-1]
        digits.append(0)
        dp = [[[0] * 2 for _ in range(2)] for _ in range(2)]
        dp[0][1][1] = 1

        for pos, target in enumerate(digits):
            ndp = [[[0] * 2 for _ in range(2)] for _ in range(2)]
            for carry in range(2):
                for aliveA in range(2):
                    for aliveB in range(2):
                        ways = dp[carry][aliveA][aliveB]
                        if not ways:
                            continue
                        if aliveA:
                            A = [(d, 1) for d in range(1, 10)]
                            if pos > 0:
                                A.append((0, 0))
                        else:
                            A = [(0, 0)]
                        if aliveB:
                            B = [(d, 1) for d in range(1, 10)]
                            if pos > 0:
                                B.append((0, 0))
                        else:
                            B = [(0, 0)]
                        for da, na in A:
                            for db, nb in B:
                                s = da + db + carry
                                if s % 10 != target:
                                    continue
                                ndp[s // 10][na][nb] += ways
            dp = ndp
        return dp[0][0][0]
# @lc code=end
