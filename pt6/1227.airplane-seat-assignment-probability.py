#
# @lc app=leetcode id=1227 lang=python3
#
# [1227] Airplane Seat Assignment Probability
#
# https://leetcode.com/problems/airplane-seat-assignment-probability/description/
#
# algorithms
# Medium (67.39%)
# Likes:    664
# Dislikes: 991
# Total Accepted:    58.5K
# Total Submissions: 86.7K
# Testcase Example:  '1'
#
# n passengers board an airplane with exactly n seats. The first passenger has
# lost the ticket and picks a seat randomly. But after that, the rest of the
# passengers will:
# 
# 
# Take their own seat if it is still available, and
# Pick other seats randomly when they find their seat occupied
# 
# 
# Return the probability that the n^th person gets his own seat.
# 
# 
# Example 1:
# 
# 
# Input: n = 1
# Output: 1.00000
# Explanation: The first person can only get the first seat.
# 
# Example 2:
# 
# 
# Input: n = 2
# Output: 0.50000
# Explanation: The second person has a probability of 0.5 to get the second
# seat (when first person gets the first seat).
# 
# 
# 
# Constraints:
# 
# 
# 1 <= n <= 10^5
# 
# 
#

# @lc code=start
class Solution:
    def nthPersonGetsNthSeat(self, n: int) -> float:
        return 1.0 if n == 1 else 0.5
# @lc code=end

# Explanation
# -----------
# For n = 1, the first passenger sits in their own seat, so the probability is
# 1. For n > 1, after passenger 1 picks a random seat, the process only cares
# about two special seats: seat 1 and seat n. If some displaced passenger later
# picks seat 1, passenger n gets seat n. If they pick seat n, passenger n loses.
# Picking any middle seat just passes the same situation to another passenger.
#
# By symmetry between the two special seats, each is the first special seat
# chosen with probability 1/2.
#
# Edge cases: n = 1 must not return 0.5; all n >= 2 return the same value.
#
# Time complexity: O(1).
# Space complexity: O(1).
