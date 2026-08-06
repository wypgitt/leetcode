#
# @lc app=leetcode id=3827 lang=python3
#
# [3827] Count Monobit Integers
#
# https://leetcode.com/problems/count-monobit-integers/description/
#
# algorithms
# Easy (66.68%)
# Likes:    56
# Dislikes: 1
# Total Accepted:    54.5K
# Total Submissions: 81.7K
# Testcase Example:  "1"
#
#
# You are given an integer n.
#
# An integer is called Monobit if all bits in its binary representation
# are the same.
#
# Return the count of Monobit integers in the range [0, n] (inclusive).
#
# Example 1:
#
# Input: n = 1
#
# Output: 2
#
# Explanation:
#
# The integers in the range [0, 1] have binary representations "0" and
# "1".
#
# Each representation consists of identical bits. Thus, the answer is 2.
#
# Example 2:
#
# Input: n = 4
#
# Output: 3
#
# Explanation:
#
# The integers in the range [0, 4] include binaries "0", "1", "10", "11",
# and "100".
#
# Only 0, 1 and 3 satisfy the Monobit condition. Thus, the answer is 3.
#
# Constraints:
#
# 0 <= n <= 1000
#

# @lc code=start

class Solution:
    def countMonobit(self, n: int) -> int:
        """
        Interview explanation:
        Monobit integers have identical bits: 0, and all-ones numbers
        1, 3, 7, 15, ... in [0, n].

        Algorithm:
        - Count 0, then generate x = (x<<1)|1 while x <= n.

        Complexity: O(log n) time, O(1) space.
        """
        ans = 1  # include 0
        x = 1
        while x <= n:
            ans += 1
            x = (x << 1) | 1
        return ans

    def countMonobit_scan(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: check each integer in [0, n] for equal bits.

        Algorithm:
        - 0 counts; for x > 0, x & (x+1) == 0 means all bits are 1.

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        for x in range(n + 1):
            if x == 0 or x & (x + 1) == 0:
                ans += 1
        return ans
# @lc code=end
