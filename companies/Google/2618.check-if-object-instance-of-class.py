#
# @lc app=leetcode id=2618 lang=python3
#
# [2618] Check if Object Instance of Class
#
# https://leetcode.com/problems/check-if-object-instance-of-class/description/
#
# algorithms
# Medium (30.10%)
# Likes:    296
# Dislikes: 111
# Total Accepted:    42.9K
# Total Submissions: 142.6K
# Testcase Example:  "() => checkIfInstanceOf(new Date(), Date)"
#
# Write a function that checks if a given value is an instance of a given class
# or superclass. For this problem, an object is considered an instance of a
# given class if that object has access to that class's methods.
#
# There are no constraints on the data types that can be passed to the function.
# For example, the value or the class could be undefined.
#
#
#
# Example 1:
#
# Input: func = () => checkIfInstanceOf(new Date(), Date)
# Output: true
# Explanation: The object returned by the Date constructor is, by definition, an
# instance of Date.
#
# Example 2:
#
# Input: func = () => { class Animal {}; class Dog extends Animal {}; return
# checkIfInstanceOf(new Dog(), Animal); }
# Output: true
# Explanation:
# class Animal {};
# class Dog extends Animal {};
# checkIfInstanceOf(new Dog(), Animal); // true
#
# Dog is a subclass of Animal. Therefore, a Dog object is an instance of both
# Dog and Animal.
#
# Example 3:
#
# Input: func = () => checkIfInstanceOf(Date, Date)
# Output: false
# Explanation: A date constructor cannot logically be an instance of itself.
#
# Example 4:
#
# Input: func = () => checkIfInstanceOf(5, Number)
# Output: true
# Explanation: 5 is a Number. Note that the "instanceof" keyword would return
# false. However, it is still considered an instance of Number because it
# accesses the Number methods. For example "toFixed()".
#

# @lc code=start
from typing import Any


def checkIfInstanceOf(obj: Any, classFunction: Any) -> bool:
    """
    Interview explanation:
    Port of JS checkIfInstanceOf: decide whether obj is an instance of
    classFunction (or a superclass), including primitives vs their types.

    Algorithm:
    - Reject non-type classFunction.
    - Use isinstance which walks the MRO for user classes and handles
      built-ins (e.g. ints vs int). Catch TypeError for odd type objects.

    Complexity: O(d) time for MRO depth d, O(1) extra space.
    """
    if not isinstance(classFunction, type):
        return False
    try:
        return isinstance(obj, classFunction)
    except TypeError:
        return False


class Solution:
    def checkIfInstanceOf(self, obj: Any, classFunction: Any) -> bool:
        """
        Interview explanation:
        Thin Solution wrapper delegating to checkIfInstanceOf.

        Algorithm:
        - Call the module-level checkIfInstanceOf helper.

        Complexity: Same as checkIfInstanceOf.
        """
        return checkIfInstanceOf(obj, classFunction)
# @lc code=end
