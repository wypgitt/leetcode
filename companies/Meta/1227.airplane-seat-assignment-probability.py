#
# @lc app=leetcode id=1227 lang=python3
#
# [1227] Airplane Seat Assignment Probability
#
# https://leetcode.com/problems/airplane-seat-assignment-probability/description/
#
# algorithms
# Medium (67.53%)
# Likes:    669
# Dislikes: 991
# Total Accepted:    61.1K
# Total Submissions: 90.5K
# Testcase Example:  "1"
#
# n passengers board an airplane with exactly n seats. The first passenger has
# lost the ticket and picks a seat randomly. But after that, the rest of the
# passengers will:
#
# Take their own seat if it is still available, and
#
# Pick other seats randomly when they find their seat occupied
#
# Return the probability that the n^th person gets his own seat.
#
# Example 1:
#
# Input: n = 1
# Output: 1.00000
# Explanation: The first person can only get the first seat.
#
# Example 2:
#
# Input: n = 2
# Output: 0.50000
# Explanation: The second person has a probability of 0.5 to get the second
# seat (when first person gets the first seat).
#
# Constraints:
#
# 1 <= n <= 10^5
#


# @lc code=start
class Solution:
    def nthPersonGetsNthSeat(self, n: int) -> float:
        """
        Interview explanation:
        Classic airplane seating: passenger 1 random; later take own or random
        among remaining. Probability nth gets own seat is 1 if n==1 else 0.5.

        Algorithm:
        - return 1.0 if n == 1 else 0.5

        Complexity: O(1).
        """
        return 1.0 if n == 1 else 0.5
# @lc code=end
