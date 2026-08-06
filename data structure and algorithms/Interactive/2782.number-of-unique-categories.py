#
# @lc app=leetcode id=2782 lang=python3
#
# [2782] Number of Unique Categories
#
# https://leetcode.com/problems/number-of-unique-categories/description/
#
# algorithms
# Medium (83.99%)
# Likes:    35
# Dislikes: 4
# Total Accepted:    3.7K
# Total Submissions: 4.4K
# Testcase Example:  "6\n[1,1,2,2,3,3]"
#
#
# You are given an integer n and an object categoryHandler of class
# CategoryHandler.
#
# There are n elements, numbered from 0 to n - 1. Each element has a
# category, and your task is to find the number of unique categories.
#
# The class CategoryHandler contains the following function, which may
# help you:
#
# boolean haveSameCategory(integer a, integer b): Returns true if a and b
# are in the same category and false otherwise. Also, if either a or b is
# not a valid number (i.e. it's greater than or equal to nor less than 0),
# it returns false.
#
# Return the number of unique categories.
#
# Example 1:
#
# Input: n = 6, categoryHandler = [1,1,2,2,3,3]
# Output: 3
# Explanation: There are 6 elements in this example. The first two
# elements belong to category 1, the second two belong to category 2, and
# the last two elements belong to category 3. So there are 3 unique
# categories.
#
# Example 2:
#
# Input: n = 5, categoryHandler = [1,2,3,4,5]
# Output: 5
# Explanation: There are 5 elements in this example. Each element belongs
# to a unique category. So there are 5 unique categories.
#
# Example 3:
#
# Input: n = 3, categoryHandler = [1,1,1]
# Output: 1
# Explanation: There are 3 elements in this example. All of them belong to
# one category. So there is only 1 unique category.
#
# Constraints:
#
# 1 <= n <= 100
#
# @lc code=start
from typing import Optional

# Definition for a category handler.
# class CategoryHandler:
#     def haveSameCategory(self, a: int, b: int) -> bool:
#         pass


try:
    CategoryHandler  # type: ignore[name-defined]
except NameError:

    class CategoryHandler:  # type: ignore[no-redef]
        def haveSameCategory(self, a: int, b: int) -> bool:
            return False


class Solution:
    def numberOfCategories(
        self, n: int, categoryHandler: Optional["CategoryHandler"]
    ) -> int:
        """
        Interview explanation:
        Premium: n elements; only API haveSameCategory(a,b). Count unique categories.

        Algorithm:
        - Union-Find: union pairs that share a category; answer = # roots.

        Complexity: O(n^2 α(n)) time, O(n) space.
        """

        def find(x: int) -> int:
            while p[x] != x:
                p[x] = p[p[x]]
                x = p[x]
            return x

        p = list(range(n))
        for a in range(n):
            for b in range(a + 1, n):
                if categoryHandler.haveSameCategory(a, b):
                    p[find(a)] = find(b)
        return sum(i == find(i) for i in range(n))

    def numberOfCategories_brute(
        self, n: int, categoryHandler: Optional["CategoryHandler"]
    ) -> int:
        """
        Interview explanation:
        Alternate: count elements that match no earlier element (new category).

        Algorithm:
        - For each i, if no j < i shares category, increment answer.

        Complexity: O(n^2) time, O(1) space.
        """
        ans = 0
        for i in range(n):
            if not any(categoryHandler.haveSameCategory(i, j) for j in range(i)):
                ans += 1
        return ans
# @lc code=end
