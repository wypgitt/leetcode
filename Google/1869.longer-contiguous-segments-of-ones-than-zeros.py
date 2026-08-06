#
# @lc app=leetcode id=1869 lang=python3
#
# [1869] Longer Contiguous Segments of Ones than Zeros
#
# https://leetcode.com/problems/longer-contiguous-segments-of-ones-than-zeros/description/
#
# algorithms
# Easy (62.65%)
# Likes:    583
# Dislikes: 14
# Total Accepted:    69.2K
# Total Submissions: 111K
# Testcase Example:  "\"1101\""
#
# Given a binary string s, return true if the longest contiguous segment of 1's
# is strictly longer than the longest contiguous segment of 0's in s, or return
# false otherwise.
#
# For example, in s = "110100010" the longest continuous segment of 1s has
# length 2, and the longest continuous segment of 0s has length 3.
#
# Note that if there are no 0's, then the longest continuous segment of 0's is
# considered to have a length 0. The same applies if there is no 1's.
#
# Example 1:
#
# Input: s = "1101"
# Output: true
# Explanation:
# The longest contiguous segment of 1s has length 2: "1101"
# The longest contiguous segment of 0s has length 1: "1101"
# The segment of 1s is longer, so return true.
#
# Example 2:
#
# Input: s = "111000"
# Output: false
# Explanation:
# The longest contiguous segment of 1s has length 3: "111000"
# The longest contiguous segment of 0s has length 3: "111000"
# The segment of 1s is not longer, so return false.
#
# Example 3:
#
# Input: s = "110100010"
# Output: false
# Explanation:
# The longest contiguous segment of 1s has length 2: "110100010"
# The longest contiguous segment of 0s has length 3: "110100010"
# The segment of 1s is not longer, so return false.
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s[i] is either '0' or '1'.
#

# @lc code=start
class Solution:
    def checkZeroOnes(self, s: str) -> bool:
        """
        Interview explanation:
        True iff longest contiguous run of '1's is strictly longer than longest
        run of '0's.

        Algorithm:
        - Scan runs; track max1, max0.

        Complexity: O(n) time, O(1) space.
        """
        max0 = max1 = cur0 = cur1 = 0
        for ch in s:
            if ch == "1":
                cur1 += 1
                cur0 = 0
                max1 = max(max1, cur1)
            else:
                cur0 += 1
                cur1 = 0
                max0 = max(max0, cur0)
        return max1 > max0

    def checkZeroOnes_split(self, s: str) -> bool:
        """
        Interview explanation:
        Alternate: split by '0' for ones runs and by '1' for zeros runs.

        Algorithm:
        - max(map(len, s.split('0'))) > max(map(len, s.split('1'))).

        Complexity: O(n) time.
        """
        return max(map(len, s.split("0"))) > max(map(len, s.split("1")))
# @lc code=end
