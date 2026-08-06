#
# @lc app=leetcode id=1884 lang=python3
#
# [1884] Egg Drop With 2 Eggs and N Floors
#
# https://leetcode.com/problems/egg-drop-with-2-eggs-and-n-floors/description/
#
# algorithms
# Medium (74.68%)
# Likes:    1555
# Dislikes: 164
# Total Accepted:    67.3K
# Total Submissions: 90.1K
# Testcase Example:  "2"
#
# You are given two identical eggs and you have access to a building with n
# floors labeled from 1 to n.
#
# You know that there exists a floor f where 0 <= f <= n such that any egg
# dropped at a floor higher than f will break, and any egg dropped at or below
# floor f will not break.
#
# In each move, you may take an unbroken egg and drop it from any floor x
# (where 1 <= x <= n). If the egg breaks, you can no longer use it. However, if
# the egg does not break, you may reuse it in future moves.
#
# Return the minimum number of moves that you need to determine with certainty
# what the value of f is.
#
# Example 1:
#
# Input: n = 2
# Output: 2
# Explanation: We can drop the first egg from floor 1 and the second egg from
# floor 2.
# If the first egg breaks, we know that f = 0.
# If the second egg breaks but the first egg didn't, we know that f = 1.
# Otherwise, if both eggs survive, we know that f = 2.
#
# Example 2:
#
# Input: n = 100
# Output: 14
# Explanation: One optimal strategy is:
# - Drop the 1st egg at floor 9. If it breaks, we know f is between 0 and 8.
# Drop the 2nd egg starting from floor 1 and going up one at a time to find f
# within 8 more drops. Total drops is 1 + 8 = 9.
# - If the 1st egg does not break, drop the 1st egg again at floor 22. If it
# breaks, we know f is between 9 and 21. Drop the 2nd egg starting from floor
# 10 and going up one at a time to find f within 12 more drops. Total drops is
# 2 + 12 = 14.
# - If the 1st egg does not break again, follow a similar process dropping the
# 1st egg from floors 34, 45, 55, 64, 72, 79, 85, 90, 94, 97, 99, and 100.
# Regardless of the outcome, it takes at most 14 drops to determine f.
#
# Constraints:
#
# 1 <= n <= 1000
#

# @lc code=start
class Solution:
    def twoEggDrop(self, n: int) -> int:
        """
        Interview explanation:
        Classic 2-egg drop: minimize worst-case drops. Optimal gaps decrease by
        1 (x + (x-1) + ... + 1 ≥ n) → smallest x with x(x+1)/2 ≥ n.

        Algorithm (math):
        - Find min x: x*(x+1)/2 >= n (binary search or loop).

        Complexity: O(sqrt(n)) or O(log n) time, O(1) space.
        """
        x = 0
        while x * (x + 1) // 2 < n:
            x += 1
        return x

    def twoEggDrop_dp(self, n: int) -> int:
        """
        Interview explanation:
        Alternate DP: dp[k][e] max floors with k drops and e eggs.
        With 2 eggs: dp[k][2] = dp[k-1][1] + 1 + dp[k-1][2] = k + dp[k-1][2].

        Algorithm:
        - Increase moves until floors covered ≥ n.

        Complexity: O(n) time.
        """
        # dp moves: covers = moves*(moves+1)/2
        moves = 0
        cover = 0
        while cover < n:
            moves += 1
            cover += moves  # +1 from 1-egg branch length
        return moves
# @lc code=end
