#
# @lc app=leetcode id=1237 lang=python3
#
# [1237] Find Positive Integer Solution for a Given Equation
#
# https://leetcode.com/problems/find-positive-integer-solution-for-a-given-equation/description/
#
# algorithms
# Medium (70.11%)
# Likes:    549
# Dislikes: 1447
# Total Accepted:    84.6K
# Total Submissions: 121K
# Testcase Example:  "1"
#
# Given a callable function f(x, y) with a hidden formula and a value z,
# reverse engineer the formula and return all positive integer pairs x and y
# where f(x,y) == z. You may return the pairs in any order.
#
# While the exact formula is hidden, the function is monotonically increasing,
# i.e.:
#
# f(x, y) < f(x + 1, y)
#
# f(x, y) < f(x, y + 1)
#
# The function interface is defined like this:
#
# interface CustomFunction {
# public:
# // Returns some positive integer f(x, y) for two positive integers x and y
# based on a formula.
# int f(int x, int y);
# };
#
# We will judge your solution as follows:
#
# The judge has a list of 9 hidden implementations of CustomFunction, along
# with a way to generate an answer key of all valid pairs for a specific z.
#
# The judge will receive two inputs: a function_id (to determine which
# implementation to test your code with), and the target z.
#
# The judge will call your findSolution and compare your results with the
# answer key.
#
# If your results match the answer key, your solution will be Accepted.
#
# Example 1:
#
# Input: function_id = 1, z = 5
# Output: [[1,4],[2,3],[3,2],[4,1]]
# Explanation: The hidden formula for function_id = 1 is f(x, y) = x + y.
# The following positive integer values of x and y make f(x, y) equal to 5:
# x=1, y=4 -> f(1, 4) = 1 + 4 = 5.
# x=2, y=3 -> f(2, 3) = 2 + 3 = 5.
# x=3, y=2 -> f(3, 2) = 3 + 2 = 5.
# x=4, y=1 -> f(4, 1) = 4 + 1 = 5.
#
# Example 2:
#
# Input: function_id = 2, z = 5
# Output: [[1,5],[5,1]]
# Explanation: The hidden formula for function_id = 2 is f(x, y) = x * y.
# The following positive integer values of x and y make f(x, y) equal to 5:
# x=1, y=5 -> f(1, 5) = 1 * 5 = 5.
# x=5, y=1 -> f(5, 1) = 5 * 1 = 5.
#
# Constraints:
#
# 1 <= function_id <= 9
#
# 1 <= z <= 100
#
# It is guaranteed that the solutions of f(x, y) == z will be in the range 1 <=
# x, y <= 1000.
#
# It is also guaranteed that f(x, y) will fit in 32 bit signed integer if 1 <=
# x, y <= 1000.
#


# @lc code=start
from typing import List

try:
    CustomFunction
except NameError:
    class CustomFunction:
        def f(self, x, y):
            return x + y

class Solution:
    def findSolution(self, customfunction: 'CustomFunction', z: int) -> List[List[int]]:
        """
        Interview explanation:
        f(x,y) monotonic increasing in both args. Two pointers: x=1,y=1000;
        if f==z record; if f<z increase x else decrease y.

        Algorithm:
        - x,y = 1,1000; while both in [1,1000]: compare f(x,y) to z and move

        Complexity: O(1000) time, O(1) extra.
        """
        ans = []
        x, y = 1, 1000
        while x <= 1000 and y >= 1:
            val = customfunction.f(x, y)
            if val == z:
                ans.append([x, y])
                x += 1
                y -= 1
            elif val < z:
                x += 1
            else:
                y -= 1
        return ans

    def findSolution_binary(self, customfunction: 'CustomFunction', z: int) -> List[List[int]]:
        """
        Interview explanation:
        Alternate: for each x binary search y such that f(x,y)==z.

        Algorithm:
        - for x in 1..1000: lo,hi binary search on y

        Complexity: O(1000 log 1000) time.
        """
        ans = []
        for x in range(1, 1001):
            lo, hi = 1, 1000
            while lo <= hi:
                mid = (lo + hi) // 2
                val = customfunction.f(x, mid)
                if val == z:
                    ans.append([x, mid])
                    break
                if val < z:
                    lo = mid + 1
                else:
                    hi = mid - 1
        return ans
# @lc code=end
