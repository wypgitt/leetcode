#
# @lc app=leetcode id=3234 lang=python3
#
# [3234] Count the Number of Substrings With Dominant Ones
#
# https://leetcode.com/problems/count-the-number-of-substrings-with-dominant-ones/description/
#
# algorithms
# Medium (41.99%)
# Likes:    649
# Dislikes: 173
# Total Accepted:    66.1K
# Total Submissions: 157.4K
# Testcase Example:  "\"00011\""
#
#
# You are given a binary string s.
#
# Return the number of substrings with dominant ones.
#
# A string has dominant ones if the number of ones in the string is
# greater than or equal to the square of the number of zeros in the
# string.
#
# Example 1:
#
# Input: s = "00011"
#
# Output: 5
#
# Explanation:
#
# The substrings with dominant ones are shown in the table below.
#
#                         i
#                         j
#                         s[i..j]
#                         Number of Zeros
#                         Number of Ones
#
#                         3
#                         3
#                         1
#                         0
#                         1
#
#                         4
#                         4
#                         1
#                         0
#                         1
#
#                         2
#                         3
#                         01
#                         1
#                         1
#
#                         3
#                         4
#                         11
#                         0
#                         2
#
#                         2
#                         4
#                         011
#                         1
#                         2
#
# Example 2:
#
# Input: s = "101101"
#
# Output: 16
#
# Explanation:
#
# The substrings with non-dominant ones are shown in the table below.
#
# Since there are 21 substrings total and 5 of them have non-dominant
# ones, it follows that there are 16 substrings with dominant ones.
#
#                         i
#                         j
#                         s[i..j]
#                         Number of Zeros
#                         Number of Ones
#
#                         1
#                         1
#                         0
#                         1
#                         0
#
#                         4
#                         4
#                         0
#                         1
#                         0
#
#                         1
#                         4
#                         0110
#                         2
#                         2
#
#                         0
#                         4
#                         10110
#                         2
#                         3
#
#                         1
#                         5
#                         01101
#                         2
#                         3
#
# Constraints:
#
# 1 <= s.length <= 4 * 10^4
#
# s consists only of characters '0' and '1'.
#

# @lc code=start
import math


class Solution:
    def numberOfSubstrings(self, s: str) -> int:
        """
        Interview explanation:
        A substring is dominant if ones >= zeros^2. zeros is at most ~sqrt(n), so
        enumerate zero-counts and slide a minimal valid window per count.

        Algorithm:
        - For each zero in 0..max feasible:
          maintain [l, r] counts; shrink while excess zeros or surplus ones.
          When count[0] == zero and ones >= zero^2, add (l - lastInvalid).

        Complexity: O(n * sqrt(n)) time, O(1) space.
        Alternate: for each start, expand until zeros^2 exceeds remaining capacity.
        """
        n = len(s)
        ans = 0
        max_zero = int((-1 + math.sqrt(1 + 4 * n)) // 2)
        for zero in range(max_zero + 1):
            last_invalid = -1
            count = [0, 0]
            l = 0
            for r, c in enumerate(s):
                count[int(c)] += 1
                while l < r:
                    if s[l] == "0" and count[0] > zero:
                        count[0] -= 1
                        last_invalid = l
                        l += 1
                    elif s[l] == "1" and count[1] - 1 >= zero * zero:
                        count[1] -= 1
                        l += 1
                    else:
                        break
                if count[0] == zero and count[1] >= zero * zero:
                    ans += l - last_invalid
        return ans

# @lc code=end
