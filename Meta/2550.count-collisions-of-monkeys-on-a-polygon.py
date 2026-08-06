#
# @lc app=leetcode id=2550 lang=python3
#
# [2550] Count Collisions of Monkeys on a Polygon
#
# https://leetcode.com/problems/count-collisions-of-monkeys-on-a-polygon/description/
#
# algorithms
# Medium (30.34%)
# Likes:    271
# Dislikes: 531
# Total Accepted:    28.1K
# Total Submissions: 92.6K
# Testcase Example:  "3"
#
# There is a regular convex polygon with n vertices. The vertices are labeled
# from 0 to n - 1 in a clockwise direction, and each vertex has exactly one
# monkey. The following figure shows a convex polygon of 6 vertices.
#
# Simultaneously, each monkey moves to a neighboring vertex. A collision happens
# if at least two monkeys reside on the same vertex after the movement or
# intersect on an edge.
#
# Return the number of ways the monkeys can move so that at least one collision
# happens. Since the answer may be very large, return it modulo 10^9 + 7.
#
#
#
# Example 1:
#
# Input: n = 3
#
# Output: 6
#
# Explanation:
#
# There are 8 total possible movements.
#
# Two ways such that they collide at some point are:
#
#
# Monkey 1 moves in a clockwise direction; monkey 2 moves in an anticlockwise
# direction; monkey 3 moves in a clockwise direction. Monkeys 1 and 2 collide.
#
#
# Monkey 1 moves in an anticlockwise direction; monkey 2 moves in an
# anticlockwise direction; monkey 3 moves in a clockwise direction. Monkeys 1
# and 3 collide.
#
# Example 2:
#
# Input: n = 4
#
# Output: 14
#
#
#
# Constraints:
#
#
# 3 <= n <= 10^9
#

# @lc code=start
class Solution:
    def monkeyMove(self, n: int) -> int:
        """
        Interview explanation:
        n monkeys on polygon vertices each move CW or CCW. Count moves with
        at least one collision, modulo 1e9+7.

        Algorithm:
        - Total configs: 2^n. Collision-free: all CW or all CCW (2 ways).
        - Answer: (2^n - 2) mod 1e9+7.

        Complexity: O(log n) time, O(1) space.
        """
        MOD = 10**9 + 7
        return (pow(2, n, MOD) - 2) % MOD

    def monkeyMove_binpow(self, n: int) -> int:
        """
        Interview explanation:
        Classic alternate: manual binary modular exponentiation for 2^n.

        Algorithm:
        - Iterative squaring; then subtract 2 mod MOD.

        Complexity: O(log n) time, O(1) space.
        """
        MOD = 10**9 + 7
        base, exp, res = 2, n, 1
        while exp:
            if exp & 1:
                res = res * base % MOD
            base = base * base % MOD
            exp >>= 1
        return (res - 2) % MOD
# @lc code=end
