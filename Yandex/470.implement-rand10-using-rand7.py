#
# @lc app=leetcode id=470 lang=python3
#
# [470] Implement Rand10() Using Rand7()
#
# https://leetcode.com/problems/implement-rand10-using-rand7/description/
#
# algorithms
# Medium (46.59%)
# Likes:    1185
# Dislikes: 389
# Total Accepted:    114K
# Total Submissions: 245K
# Testcase Example:  "1"
#
# Given the API rand7() that generates a uniform random integer in the range
# [1, 7], write a function rand10() that generates a uniform random integer in
# the range [1, 10]. You can only call the API rand7(), and you shouldn't call
# any other API. Please do not use a language's built-in random API.
#
# Each test case will have one internal argument n, the number of times that
# your implemented function rand10() will be called while testing. Note that
# this is not an argument passed to rand10().
#
# Example 1:
#
# Input: n = 1
# Output: [2]
#
# Example 2:
#
# Input: n = 2
# Output: [2,8]
#
# Example 3:
#
# Input: n = 3
# Output: [3,8,10]
#
# Constraints:
#
# 1 <= n <= 10^5
#
# Follow up:
#
# What is the expected value for the number of calls to rand7() function?
#
# Could you minimize the number of calls to rand7()?
#

# @lc code=start
# The rand7() API is already defined for you.
# def rand7():
# @return a random integer in the range 1 to 7

# LeetCode provides rand7() globally. Local stub for py_compile only.
try:
    rand7  # type: ignore[name-defined]
except NameError:
    def rand7() -> int:
        return 1


class Solution:
    def rand10(self) -> int:
        """
        Interview explanation:
        Rejection sampling: generate uniform in [1,49] via (rand7-1)*7+rand7.
        Accept values 1..40 → map to 1..10; reject 41..49 and retry. Preserves
        uniformity because 40 is divisible by 10.

        Algorithm:
        - Loop: a,b = rand7(), rand7(); idx = (a-1)*7 + b  (1..49)
        - If idx <= 40: return (idx-1) % 10 + 1; else retry.

        Complexity: Expected O(1) rand7 calls (~2.45), O(1) space.
        """
        while True:
            idx = (rand7() - 1) * 7 + rand7()
            if idx <= 40:
                return (idx - 1) % 10 + 1
# @lc code=end
