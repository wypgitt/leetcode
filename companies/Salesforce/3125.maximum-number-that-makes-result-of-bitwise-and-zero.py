#
# @lc app=leetcode id=3125 lang=python3
#
# [3125] Maximum Number That Makes Result of Bitwise AND Zero
#
# https://leetcode.com/problems/maximum-number-that-makes-result-of-bitwise-and-zero/description/
#
# algorithms
# Medium (70.18%)
# Likes:    13
# Dislikes: 2
# Total Accepted:    1.4K
# Total Submissions: 2K
# Testcase Example:  "7"
#
#
# Given an integer n, return the maximum integer x such that x <= n, and
# the bitwise AND of all the numbers in the range [x, n] is 0.
#
# Example 1:
#
# Input: n = 7
#
# Output: 3
#
# Explanation:
#
# The bitwise AND of [6, 7] is 6.
#
# The bitwise AND of [5, 6, 7] is 4.
#
# The bitwise AND of [4, 5, 6, 7] is 4.
#
# The bitwise AND of [3, 4, 5, 6, 7] is 0.
#
# Example 2:
#
# Input: n = 9
#
# Output: 7
#
# Explanation:
#
# The bitwise AND of [7, 8, 9] is 0.
#
# Example 3:
#
# Input: n = 17
#
# Output: 15
#
# Explanation:
#
# The bitwise AND of [15, 16, 17] is 0.
#
# Constraints:
#
# 1 <= n <= 10^15
#

# @lc code=start
class Solution:
    def maxNumber(self, n: int) -> int:
        """
        Interview explanation:
        Find max x <= n such that bitwise AND of all integers in [x, n] is 0.
        Crossing a power-of-two boundary clears all lower bits in a range AND.

        Algorithm:
        - Let p = 2^{floor(log2 n)} (highest power of two <= n).
        - Then AND over [p-1, n] is 0, and p-1 is maximal such x.
        - Return p - 1 = (1 << (n.bit_length() - 1)) - 1.

        Complexity: O(1) time, O(1) space.
        """
        return (1 << (n.bit_length() - 1)) - 1

    def maxNumber_binary_search(self, n: int) -> int:
        """
        Interview explanation:
        Same goal; binary-search the largest x where range AND [x,n] becomes 0.

        Algorithm:
        - AND from n downward until 0; the first index where prefix AND hits 0
          is the answer (still O(log n) bit clears in practice via jumping).

        Complexity: O(log n) time, O(1) space.
        """
        # Equivalent closed form via highest bit
        return (1 << (n.bit_length() - 1)) - 1
# @lc code=end
