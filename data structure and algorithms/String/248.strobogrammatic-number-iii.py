#
# @lc app=leetcode id=248 lang=python3
#
# [248] Strobogrammatic Number III
#
# https://leetcode.com/problems/strobogrammatic-number-iii/description/
#
# algorithms
# Hard (42.70%)
# Likes:    308
# Dislikes: 193
# Total Accepted:    38.5K
# Total Submissions: 90.1K
# Testcase Example:  "\"50\"\n\"100\""
#
#
# Given two strings low and high that represent two integers low and high
# where low <= high, return the number of strobogrammatic numbers in the
# range [low, high].
#
# A strobogrammatic number is a number that looks the same when rotated
# 180 degrees (looked at upside down).
#
# Example 1:
#
# Input: low = "50", high = "100"
# Output: 3
#
# Example 2:
#
# Input: low = "0", high = "0"
# Output: 1
#
# Constraints:
#
# 1 <= low.length, high.length <= 15
#
# low and high consist of only digits.
#
# low <= high
#
# low and high do not contain any leading zeros except for zero itself.
#
# @lc code=start
class Solution:
    def strobogrammaticInRange(self, low: str, high: str) -> int:
        """
        Interview explanation:
        Count strobogrammatic numbers with length between len(low) and len(high)
        by DFS-constructing valid numbers digit-pair by digit-pair, then checking
        the numeric range [low, high] as strings (same length compare).

        Algorithm:
        - Pairs: (0,0),(1,1),(6,9),(8,8),(9,6); singles for odd length: 0,1,8.
        - For each length L in [len(low), len(high)], DFS fill positions.
        - Accept strings that don't have leading zeros (unless "0") and lie in range.

        Complexity: O(5^{L/2} * L) over relevant lengths; space O(L) recursion.
        """
        pairs = [("0", "0"), ("1", "1"), ("6", "9"), ("8", "8"), ("9", "6")]
        centers = ["0", "1", "8"]

        def in_range(s: str) -> bool:
            if len(s) < len(low) or len(s) > len(high):
                return False
            if len(s) == len(low) and s < low:
                return False
            if len(s) == len(high) and s > high:
                return False
            return True

        def dfs(left: int, right: int, chars: list) -> int:
            if left > right:
                s = "".join(chars)
                if len(s) > 1 and s[0] == "0":
                    return 0
                return 1 if in_range(s) else 0
            count = 0
            if left == right:
                for c in centers:
                    chars[left] = c
                    count += dfs(left + 1, right - 1, chars)
                return count
            for a, b in pairs:
                chars[left] = a
                chars[right] = b
                count += dfs(left + 1, right - 1, chars)
            return count

        total = 0
        for length in range(len(low), len(high) + 1):
            total += dfs(0, length - 1, [""] * length)
        return total
# @lc code=end
