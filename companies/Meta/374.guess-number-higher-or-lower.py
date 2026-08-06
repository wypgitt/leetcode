#
# @lc app=leetcode id=374 lang=python3
#
# [374] Guess Number Higher or Lower
#
# https://leetcode.com/problems/guess-number-higher-or-lower/description/
#
# algorithms
# Easy (58.05%)
# Likes:    4322
# Dislikes: 702
# Total Accepted:    1.1M
# Total Submissions: 1.8M
# Testcase Example:  "10"
#
# We are playing the Guess Game. The game is as follows:
#
# I pick a number from 1 to n. You have to guess which number I picked (the
# number I picked stays the same throughout the game).
#
# Every time you guess wrong, I will tell you whether the number I picked is
# higher or lower than your guess.
#
# You call a pre-defined API int guess(int num), which returns three possible
# results:
#
# -1: Your guess is higher than the number I picked (i.e. num > pick).
#
# 1: Your guess is lower than the number I picked (i.e. num < pick).
#
# 0: your guess is equal to the number I picked (i.e. num == pick).
#
# Return the number that I picked.
#
# Example 1:
#
# Input: n = 10, pick = 6
# Output: 6
#
# Example 2:
#
# Input: n = 1, pick = 1
# Output: 1
#
# Example 3:
#
# Input: n = 2, pick = 1
# Output: 1
#
# Constraints:
#
# 1 <= n <= 2^31 - 1
#
# 1 <= pick <= n
#

# @lc code=start
# The guess API is already defined for you.
# @param num, your guess
# @return -1 if num is higher than the picked number
#          1 if num is lower than the picked number
#          otherwise return 0
# def guess(num: int) -> int:

# LeetCode provides guess() globally. Local stub for py_compile only.
try:
    guess  # type: ignore[name-defined]
except NameError:
    def guess(num: int) -> int:
        return 0


class Solution:
    def guessNumber(self, n: int) -> int:
        """
        Interview explanation:
        Binary search on [1, n]. Each mid query via guess API tells whether
        the pick is lower, higher, or equal — classic lower/upper half shrink.

        Algorithm:
        - lo, hi = 1, n
        - mid = (lo + hi) // 2; res = guess(mid)
        - res == 0 -> return mid; res < 0 -> hi = mid-1; else lo = mid+1

        Complexity: O(log n) guesses, O(1) space.
        """
        lo, hi = 1, n
        while lo <= hi:
            mid = (lo + hi) // 2
            res = guess(mid)
            if res == 0:
                return mid
            if res < 0:
                hi = mid - 1
            else:
                lo = mid + 1
        return lo
# @lc code=end
