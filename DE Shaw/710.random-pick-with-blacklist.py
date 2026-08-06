#
# @lc app=leetcode id=710 lang=python3
#
# [710] Random Pick with Blacklist
#
# https://leetcode.com/problems/random-pick-with-blacklist/description/
#
# algorithms
# Hard (35.31%)
# Likes:    903
# Dislikes: 121
# Total Accepted:    54.7K
# Total Submissions: 155K
# Testcase Example:  "[\"Solution\",\"pick\",\"pick\",\"pick\",\"pick\",\"pick\",\"pick\",\"pick\"]"
#
# You are given an integer n and an array of unique integers blacklist. Design
# an algorithm to pick a random integer in the range [0, n - 1] that is not in
# blacklist. Any integer that is in the mentioned range and not in blacklist
# should be equally likely to be returned.
#
# Optimize your algorithm such that it minimizes the number of calls to the
# built-in random function of your language.
#
# Implement the Solution class:
#
# Solution(int n, int[] blacklist) Initializes the object with the integer n
# and the blacklisted integers blacklist.
#
# int pick() Returns a random integer in the range [0, n - 1] and not in
# blacklist.
#
# Example 1:
#
# Input
# ["Solution", "pick", "pick", "pick", "pick", "pick", "pick", "pick"]
# [[7, [2, 3, 5]], [], [], [], [], [], [], []]
# Output
# [null, 0, 4, 1, 6, 1, 0, 4]
#
# Explanation
# Solution solution = new Solution(7, [2, 3, 5]);
# solution.pick(); // return 0, any integer from [0,1,4,6] should be ok. Note
# that for every call of pick,
# // 0, 1, 4, and 6 must be equally likely to be returned (i.e., with
# probability 1/4).
# solution.pick(); // return 4
# solution.pick(); // return 1
# solution.pick(); // return 6
# solution.pick(); // return 1
# solution.pick(); // return 0
# solution.pick(); // return 4
#
# Constraints:
#
# 1 <= n <= 10^9
#
# 0 <= blacklist.length <= min(10^5, n - 1)
#
# 0 <= blacklist[i] < n
#
# All the values of blacklist are unique.
#
# At most 2 * 10^4 calls will be made to pick.
#

# @lc code=start
import random
from typing import List


class Solution:
    def __init__(self, n: int, blacklist: List[int]):
        """
        Interview explanation:
        Pick uniformly from [0, n) excluding blacklist in O(1). Remap blacklisted
        indices in the whitelist prefix [0, M) to white indices in [M, n).

        Algorithm:
        - M = n - len(blacklist). Black set; map each black b < M to a white
          w >= M (scan from n-1 downward).

        Complexity: O(B) init time/space.
        """
        self.M = n - len(blacklist)
        black = set(blacklist)
        self.remap = {}
        w = n - 1
        for b in blacklist:
            if b < self.M:
                while w in black:
                    w -= 1
                self.remap[b] = w
                w -= 1

    def pick(self) -> int:
        """
        Interview explanation:
        Sample x uniformly in [0, M); return remap[x] if remapped else x.

        Algorithm:
        - x = randint(0, M-1); return self.remap.get(x, x).

        Complexity: O(1) time.
        """
        x = random.randint(0, self.M - 1)
        return self.remap.get(x, x)


# Your Solution object will be instantiated and called as such:
# obj = Solution(n, blacklist)
# param_1 = obj.pick()
# @lc code=end
