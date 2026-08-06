#
# @lc app=leetcode id=1291 lang=python3
#
# [1291] Sequential Digits
#
# https://leetcode.com/problems/sequential-digits/description/
#
# algorithms
# Medium (68.63%)
# Likes:    3240
# Dislikes: 183
# Total Accepted:    356K
# Total Submissions: 518K
# Testcase Example:  "100"
#
# An integer has sequential digits if and only if each digit in the number is
# one more than the previous digit.
#
# Return a sorted list of all the integers in the range [low, high] inclusive
# that have sequential digits.
#
# Example 1:
#
# Input: low = 100, high = 300
# Output: [123,234]
#
# Example 2:
#
# Input: low = 1000, high = 13000
# Output: [1234,2345,3456,4567,5678,6789,12345]
#
# Constraints:
#
# 10 <= low <= high <= 10^9
#

# @lc code=start

from typing import List
from collections import deque


class Solution:
    def sequentialDigits(self, low: int, high: int) -> List[int]:
        """
        Interview explanation:
        Sequential-digit numbers are contiguous substrings of "123456789".
        Enumerate by increasing length so results are sorted; keep those in
        [low, high].

        Algorithm:
        - digits='123456789'; for length 2..9 and each start index, form num;
          append while <=high and >=low.

        Complexity: O(1) (≤36 candidates).
        """
        digits = "123456789"
        ans = []
        for length in range(2, 10):
            for i in range(0, 10 - length):
                num = int(digits[i : i + length])
                if num < low:
                    continue
                if num > high:
                    return ans
                ans.append(num)
        return ans

    def sequentialDigits_bfs(self, low: int, high: int) -> List[int]:
        """
        Interview explanation:
        Alternate BFS generation: start from 1..9; append next digit last+1.

        Algorithm:
        - Queue 1..9; while queue: if in range and >=10 append; extend by +1 digit.

        Complexity: O(1).
        """
        q = deque(range(1, 10))
        ans = []
        while q:
            num = q.popleft()
            if low <= num <= high and num >= 10:
                ans.append(num)
            last = num % 10
            if last < 9:
                nxt = num * 10 + last + 1
                if nxt <= high:
                    q.append(nxt)
        return ans
# @lc code=end
