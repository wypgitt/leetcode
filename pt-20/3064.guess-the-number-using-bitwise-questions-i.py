#
# @lc app=leetcode id=3064 lang=python3
#
# [3064] Guess the Number Using Bitwise Questions I
#
# https://leetcode.com/problems/guess-the-number-using-bitwise-questions-i/description/
#
# algorithms
# Medium (88.91%)
# Likes:    12
# Dislikes: 11
# Total Accepted:    2.4K
# Total Submissions: 2.7K
# Testcase Example:  "31"
#
#
# There is a number n that you have to find.
#
# There is also a pre-defined API int commonSetBits(int num), which
# returns the number of bits where both n and num are 1 in that position
# of their binary representation. In other words, it returns the number of
# set bits in n & num, where & is the bitwise AND operator.
#
# Return the number n.
#
# Example 1:
#
# Input:   n = 31
#
# Output:   31
#
# Explanation:  It can be proven that it's possible to find 31 using the
# provided API.
#
# Example 2:
#
# Input:   n = 33
#
# Output:   33
#
# Explanation:  It can be proven that it's possible to find 33 using the
# provided API.
#
# Constraints:
#
# 1 <= n <= 2^30 - 1
#
# 0 <= num <= 2^30 - 1
#
# If you ask for some num out of the given range, the output wouldn't be
# reliable.
#

# @lc code=start
# Definition of commonSetBits API.
# def commonSetBits(num: int) -> int:

try:
    commonSetBits  # type: ignore[name-defined]
except NameError:

    def commonSetBits(num: int) -> int:  # type: ignore[misc]
        return 0


class Solution:
    def findNumber(self) -> int:
        """
        Interview explanation:
        Interactive: commonSetBits(num) = popcount(n & num). Recover unknown n
        in [1, 2^30 - 1] by probing each bit independently.

        Algorithm:
        - For bit i in 0..29, query commonSetBits(1 << i); if 1, set that bit.

        Complexity: O(1) queries (30), O(1) space.
        """
        n = 0
        for i in range(30):
            if commonSetBits(1 << i) == 1:
                n |= 1 << i
        return n

    def findNumber_accumulate(self) -> int:
        """
        Interview explanation:
        Alternate: ask with single-bit masks and accumulate via addition.

        Algorithm:
        - Same bit probes; add (1 << i) when the API reports a shared set bit.

        Complexity: O(1) queries, O(1) space.
        """
        return sum((1 << i) for i in range(30) if commonSetBits(1 << i) == 1)
# @lc code=end
