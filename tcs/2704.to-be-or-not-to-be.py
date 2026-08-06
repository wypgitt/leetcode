#
# @lc app=leetcode id=2704 lang=python3
#
# [2704] To Be Or Not To Be
#
# https://leetcode.com/problems/to-be-or-not-to-be/description/
#
# algorithms
# Easy (63.40%)
# Likes:    944
# Dislikes: 225
# Total Accepted:    369.2K
# Total Submissions: 582.4K
# Testcase Example:  "() => expect(5).toBe(5)"
#
# Write a function expect that helps developers test their code. It should take
# in any value val and return an object with the following two functions.
#
#
# toBe(val) accepts another value and returns true if the two values === each
# other. If they are not equal, it should throw an error "Not Equal".
#
#
# notToBe(val) accepts another value and returns true if the two values !== each
# other. If they are equal, it should throw an error "Equal".
#
#
#
# Example 1:
#
# Input: func = () => expect(5).toBe(5)
# Output: {"value": true}
# Explanation: 5 === 5 so this expression returns true.
#
# Example 2:
#
# Input: func = () => expect(5).toBe(null)
# Output: {"error": "Not Equal"}
# Explanation: 5 !== null so this expression throw the error "Not Equal".
#
# Example 3:
#
# Input: func = () => expect(5).notToBe(null)
# Output: {"value": true}
# Explanation: 5 !== null so this expression returns true.
#

# @lc code=start
from typing import Any


class Expect:
    def __init__(self, val: Any) -> None:
        """
        Interview explanation:
        Hold a value under test for toBe / notToBe assertions.

        Algorithm:
        - Store val.

        Complexity: O(1).
        """
        self.val = val

    def toBe(self, expected: Any) -> bool:
        """
        Interview explanation:
        Assert equality; raise "Not Equal" on mismatch.

        Algorithm:
        - Compare with ==; return True or raise Exception("Not Equal").

        Complexity: O(1) for typical scalars.
        """
        if self.val == expected:
            return True
        raise Exception("Not Equal")

    def notToBe(self, expected: Any) -> bool:
        """
        Interview explanation:
        Assert inequality; raise "Equal" on match.

        Algorithm:
        - Compare with !=; return True or raise Exception("Equal").

        Complexity: O(1) for typical scalars.
        """
        if self.val != expected:
            return True
        raise Exception("Equal")


def expect(val: Any) -> Expect:
    """
    Interview explanation:
    JavaScript problem (Python analog): return an assertion object for val.

    Algorithm:
    - Wrap val in Expect.

    Complexity: O(1).
    """
    return Expect(val)


class Solution:
    def expect(self, val: Any) -> Expect:
        """
        Interview explanation:
        Solution wrapper calling module-level expect.

        Algorithm:
        - Return Expect(val).

        Complexity: O(1).
        """
        return expect(val)
# @lc code=end
