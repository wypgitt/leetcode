#
# @lc app=leetcode id=3228 lang=python3
#
# [3228] Maximum Number of Operations to Move Ones to the End
#
# https://leetcode.com/problems/maximum-number-of-operations-to-move-ones-to-the-end/description/
#
# algorithms
# Medium (67.13%)
# Likes:    535
# Dislikes: 39
# Total Accepted:    126.2K
# Total Submissions: 188K
# Testcase Example:  "\"1001101\""
#
#
# You are given a binary string s.
#
# You can perform the following operation on the string any number of
# times:
#
# Choose any index i from the string where i + 1 < s.length such that s[i]
# == '1' and s[i + 1] == '0'.
#
# Move the character s[i] to the right until it reaches the end of the
# string or another '1'. For example, for s = "010010", if we choose i =
# 1, the resulting string will be s = "000110".
#
# Return the maximum number of operations that you can perform.
#
# Example 1:
#
# Input: s = "1001101"
#
# Output: 4
#
# Explanation:
#
# We can perform the following operations:
#
# Choose index i = 0. The resulting string is s = "0011101".
#
# Choose index i = 4. The resulting string is s = "0011011".
#
# Choose index i = 3. The resulting string is s = "0010111".
#
# Choose index i = 2. The resulting string is s = "0001111".
#
# Example 2:
#
# Input: s = "00111"
#
# Output: 0
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s[i] is either '0' or '1'.
#

# @lc code=start
class Solution:
    def maxOperations(self, s: str) -> int:
        """
        Interview explanation:
        An operation slides a '1' right through a run of zeros until the next '1'.
        Maximizing ops means greedily moving every left '1' across every zero-run
        that appears to its right.

        Algorithm:
        - Scan left to right; accumulate ones seen so far.
        - When a zero-run follows a ones-run (i.e., we finish a ones streak and
          the next char is '0'), add the current ones count to the answer.

        Complexity: O(n) time, O(1) space.
        Alternate: count zero-groups after the first one and weight by ones.
        """
        ans = ones = 0
        i, n = 0, len(s)
        while i < n:
            if s[i] == "0":
                i += 1
                continue
            j = i
            while j < n and s[j] == "1":
                j += 1
            ones += j - i
            if j < n:
                ans += ones
            i = j
        return ans

# @lc code=end
