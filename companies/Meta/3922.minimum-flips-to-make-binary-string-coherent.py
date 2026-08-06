#
# @lc app=leetcode id=3922 lang=python3
#
# [3922] Minimum Flips to Make Binary String Coherent
#
# https://leetcode.com/problems/minimum-flips-to-make-binary-string-coherent/description/
#
# algorithms
# Medium (20.07%)
# Likes:    55
# Dislikes: 7
# Total Accepted:    16.5K
# Total Submissions: 82.3K
# Testcase Example:  "\"1010\""
#
#
# You are given a binary string s.
#
# A string is considered coherent if it does not contain "011" or "110" as
# subsequences.
#
# In one operation, you can flip any character in s ('0' to '1' or '1' to
# '0').
#
# Return an integer denoting the minimum number of operations required to
# make s coherent.
#
# Example 1:
#
# Input: s = "1010"
#
# Output: 1
#
# Explanation:
#
# Flip s[0] to get "0010", which contains no "011" or "110" subsequences.
#
# Example 2:
#
# Input: s = "0110"
#
# Output: 1
#
# Explanation:
#
# Flip s[1] to get "0010", removing all forbidden subsequences "011" and
# "110".
#
# Example 3:
#
# Input: s = "1000"
#
# Output: 0
#
# Explanation:
#
# The string already has no "011" or "110" subsequences, so no flips are
# needed.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s[i] is either '0' or '1'.
#

# @lc code=start
class Solution:
    def minFlips(self, s: str) -> int:
        """
        Interview explanation:
        Coherent strings forbid subsequences 011 and 110. Allowed forms are:
        ≤1 ones, all ones, or exactly 10…01 spanning the whole string.

        Algorithm:
        - Cost to ≤1 one: max(0, ones-1); cost to all ones: zeros.
        - If both ends are already '1', also try clearing middle ones (form 10…01).
        - Return the minimum of these options.

        Complexity: O(n) time, O(1) space.
        """
        ones = s.count("1")
        zeros = len(s) - ones
        ans = min(max(0, ones - 1), zeros)
        if len(s) >= 2 and s[0] == "1" and s[-1] == "1":
            ans = min(ans, s[1:-1].count("1"))
        return ans
# @lc code=end
