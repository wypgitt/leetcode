#
# @lc app=leetcode id=3133 lang=python3
#
# [3133] Minimum Array End
#
# https://leetcode.com/problems/minimum-array-end/description/
#
# algorithms
# Medium (55.29%)
# Likes:    826
# Dislikes: 100
# Total Accepted:    112K
# Total Submissions: 202.5K
# Testcase Example:  "3\n4"
#
#
# You are given two integers n and x. You have to construct an array of
# positive integers nums of size n where for every 0 <= i < n - 1, nums[i
# + 1] is greater than nums[i], and the result of the bitwise AND
# operation between all elements of nums is x.
#
# Return the minimum possible value of nums[n - 1].
#
# Example 1:
#
# Input: n = 3, x = 4
#
# Output: 6
#
# Explanation:
#
# nums can be [4,5,6] and its last element is 6.
#
# Example 2:
#
# Input: n = 2, x = 7
#
# Output: 15
#
# Explanation:
#
# nums can be [7,15] and its last element is 15.
#
# Constraints:
#
# 1 <= n, x <= 10^8
#

# @lc code=start
class Solution:
    def minEnd(self, n: int, x: int) -> int:
        """
        Interview explanation:
        Build a strictly increasing length-n array whose AND is x; minimize the
        last element. Every nums[i] must keep all bits of x set; free bits
        (unset in x) encode the n distinct values.

        Algorithm:
        - Start from x. Write the bits of (n-1) into the zero-bits of x (from
          low to high). That yields the smallest last value of an n-element
          AND-x chain.

        Complexity: O(log n + log x) time, O(1) space.
        """
        n -= 1
        ans = x
        bit = 0
        while n:
            if ((x >> bit) & 1) == 0:
                if n & 1:
                    ans |= 1 << bit
                n >>= 1
            bit += 1
        return ans
# @lc code=end
