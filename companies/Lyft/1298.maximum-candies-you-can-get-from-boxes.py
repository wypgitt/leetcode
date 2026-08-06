#
# @lc app=leetcode id=1298 lang=python3
#
# [1298] Maximum Candies You Can Get from Boxes
#
# https://leetcode.com/problems/maximum-candies-you-can-get-from-boxes/description/
#
# algorithms
# Hard (67.12%)
# Likes:    786
# Dislikes: 228
# Total Accepted:    109K
# Total Submissions: 163K
# Testcase Example:  "[1,0,1,0]"
#
# You have n boxes labeled from 0 to n - 1. You are given four arrays: status,
# candies, keys, and containedBoxes where:
#
# status[i] is 1 if the i^th box is open and 0 if the i^th box is closed,
#
# candies[i] is the number of candies in the i^th box,
#
# keys[i] is a list of the labels of the boxes you can open after opening the
# i^th box.
#
# containedBoxes[i] is a list of the boxes you found inside the i^th box.
#
# You are given an integer array initialBoxes that contains the labels of the
# boxes you initially have. You can take all the candies in any open box and
# you can use the keys in it to open new boxes and you also can use the boxes
# you find in it.
#
# Return the maximum number of candies you can get following the rules above.
#
# Example 1:
#
# Input: status = [1,0,1,0], candies = [7,5,4,100], keys = [[],[],[1],[]],
# containedBoxes = [[1,2],[3],[],[]], initialBoxes = [0]
# Output: 16
# Explanation: You will be initially given box 0. You will find 7 candies in it
# and boxes 1 and 2.
# Box 1 is closed and you do not have a key for it so you will open box 2. You
# will find 4 candies and a key to box 1 in box 2.
# In box 1, you will find 5 candies and box 3 but you will not find a key to
# box 3 so box 3 will remain closed.
# Total number of candies collected = 7 + 4 + 5 = 16 candy.
#
# Example 2:
#
# Input: status = [1,0,0,0,0,0], candies = [1,1,1,1,1,1], keys =
# [[1,2,3,4,5],[],[],[],[],[]], containedBoxes = [[1,2,3,4,5],[],[],[],[],[]],
# initialBoxes = [0]
# Output: 6
# Explanation: You have initially box 0. Opening it you can find boxes 1,2,3,4
# and 5 and their keys.
# The total number of candies will be 6.
#
# Constraints:
#
# n == status.length == candies.length == keys.length == containedBoxes.length
#
# 1 <= n <= 1000
#
# status[i] is either 0 or 1.
#
# 1 <= candies[i] <= 1000
#
# 0 <= keys[i].length <= n
#
# 0 <= keys[i][j] < n
#
# All values of keys[i] are unique.
#
# 0 <= containedBoxes[i].length <= n
#
# 0 <= containedBoxes[i][j] < n
#
# All values of containedBoxes[i] are unique.
#
# Each box is contained in one box at most.
#
# 0 <= initialBoxes.length <= n
#
# 0 <= initialBoxes[i] < n
#

# @lc code=start

from typing import List
from collections import deque


class Solution:
    def maxCandies(
        self,
        status: List[int],
        candies: List[int],
        keys: List[List[int]],
        containedBoxes: List[List[int]],
        initialBoxes: List[int],
    ) -> int:
        """
        Interview explanation:
        Open boxes you have that are open (or become open via keys). BFS/queue
        of boxes you possess; if status open, take candies, gain keys (may
        open previously held locked boxes), and gain contained boxes.

        Algorithm:
        - have=set(initial); q=deque of boxes in have with status 1.
        - seen opened set; while q: open box, add candies, mark keys status=1,
          enqueue newly openable held boxes; add contained boxes to have.

        Complexity: O(n + total keys/boxes edges).
        """
        n = len(status)
        have = set(initialBoxes)
        opened = set()
        q = deque([b for b in initialBoxes if status[b] == 1])
        ans = 0
        while q:
            b = q.popleft()
            if b in opened:
                continue
            opened.add(b)
            ans += candies[b]
            for k in keys[b]:
                status[k] = 1
                if k in have and k not in opened:
                    q.append(k)
            for nb in containedBoxes[b]:
                have.add(nb)
                if status[nb] == 1 and nb not in opened:
                    q.append(nb)
        return ans
# @lc code=end
