#
# @lc app=leetcode id=2375 lang=python3
#
# [2375] Construct Smallest Number From DI String
#
# https://leetcode.com/problems/construct-smallest-number-from-di-string/description/
#
# algorithms
# Medium (85.50%)
# Likes:    1680
# Dislikes: 89
# Total Accepted:    171.3K
# Total Submissions: 200.4K
# Testcase Example:  "\"IIIDIDDD\""
#
# You are given a 0-indexed string pattern of length n consisting of the
# characters 'I' meaning increasing and 'D' meaning decreasing.
#
# A 0-indexed string num of length n + 1 is created using the following
# conditions:
#
#
# num consists of the digits '1' to '9', where each digit is used at most once.
#
#
# If pattern[i] == 'I', then num[i] < num[i + 1].
#
#
# If pattern[i] == 'D', then num[i] > num[i + 1].
#
# Return the lexicographically smallest possible string num that meets the
# conditions.
#
#
#
# Example 1:
#
# Input: pattern = "IIIDIDDD"
# Output: "123549876"
# Explanation:
# At indices 0, 1, 2, and 4 we must have that num[i] < num[i+1].
# At indices 3, 5, 6, and 7 we must have that num[i] > num[i+1].
# Some possible values of num are "245639871", "135749862", and "123849765".
# It can be proven that "123549876" is the smallest possible num that meets the
# conditions.
# Note that "123414321" is not possible because the digit '1' is used more than
# once.
#
# Example 2:
#
# Input: pattern = "DDD"
# Output: "4321"
# Explanation:
# Some possible values of num are "9876", "7321", and "8742".
# It can be proven that "4321" is the smallest possible num that meets the
# conditions.
#
#
#
# Constraints:
#
#
# 1 <= pattern.length <= 8
#
#
# pattern consists of only the letters 'I' and 'D'.
#

# @lc code=start

class Solution:
    def smallestNumber(self, pattern: str) -> str:
        """
        Interview explanation:
        Build permutation of 1..n+1 matching 'I'/'D' between adjacent digits;
        return lexicographically smallest as string.

        Algorithm:
        - Stack: for each position push digit; on 'I' or end, pop stack to ans
          (reverses D-runs).

        Complexity: O(n) time, O(n) space.
        """
        n = len(pattern)
        ans = []
        stack = []
        for i in range(n + 1):
            stack.append(str(i + 1))
            if i == n or pattern[i] == 'I':
                while stack:
                    ans.append(stack.pop())
        return ''.join(ans)

    def smallestNumber_backtrack(self, pattern: str) -> str:
        """
        Interview explanation:
        Alternate: backtracking first valid permutation in order (also smallest).

        Algorithm:
        - Try unused digits 1..9; prune if last comparison fails DI constraint.

        Complexity: O(n!) worst, O(n) space; fine for n<=8.
        """
        n = len(pattern)
        used = [False] * 10
        path = []

        def ok(i: int, d: int) -> bool:
            if i == 0:
                return True
            prev = path[-1]
            if pattern[i - 1] == 'I':
                return prev < d
            return prev > d

        def dfs(i: int) -> bool:
            if i == n + 1:
                return True
            for d in range(1, n + 2):
                if used[d] or not ok(i, d):
                    continue
                used[d] = True
                path.append(d)
                if dfs(i + 1):
                    return True
                path.pop()
                used[d] = False
            return False

        dfs(0)
        return ''.join(map(str, path))
# @lc code=end
