#
# @lc app=leetcode id=2162 lang=python3
#
# [2162] Minimum Cost to Set Cooking Time
#
# https://leetcode.com/problems/minimum-cost-to-set-cooking-time/description/
#
# algorithms
# Medium (45.02%)
# Likes:    238
# Dislikes: 650
# Total Accepted:    23.9K
# Total Submissions: 53.1K
# Testcase Example:  "1\n2\n1\n600"
#
# A generic microwave supports cooking times for:
#
#
# at least 1 second.
#
#
# at most 99 minutes and 99 seconds.
#
# To set the cooking time, you push at most four digits. The microwave
# normalizes what you push as four digits by prepending zeroes. It interprets
# the first two digits as the minutes and the last two digits as the seconds. It
# then adds them up as the cooking time. For example,
#
#
# You push 9 5 4 (three digits). It is normalized as 0954 and interpreted as 9
# minutes and 54 seconds.
#
#
# You push 0 0 0 8 (four digits). It is interpreted as 0 minutes and 8 seconds.
#
#
# You push 8 0 9 0. It is interpreted as 80 minutes and 90 seconds.
#
#
# You push 8 1 3 0. It is interpreted as 81 minutes and 30 seconds.
#
# You are given integers startAt, moveCost, pushCost, and targetSeconds.
# Initially, your finger is on the digit startAt. Moving the finger above any
# specific digit costs moveCost units of fatigue. Pushing the digit below the
# finger once costs pushCost units of fatigue.
#
# There can be multiple ways to set the microwave to cook for targetSeconds
# seconds but you are interested in the way with the minimum cost.
#
# Return the minimum cost to set targetSeconds seconds of cooking time.
#
# Remember that one minute consists of 60 seconds.
#
#
#
# Example 1:
#
# Input: startAt = 1, moveCost = 2, pushCost = 1, targetSeconds = 600
# Output: 6
# Explanation: The following are the possible ways to set the cooking time.
# - 1 0 0 0, interpreted as 10 minutes and 0 seconds.
#   The finger is already on digit 1, pushes 1 (with cost 1), moves to 0 (with
# cost 2), pushes 0 (with cost 1), pushes 0 (with cost 1), and pushes 0 (with
# cost 1).
#   The cost is: 1 + 2 + 1 + 1 + 1 = 6. This is the minimum cost.
# - 0 9 6 0, interpreted as 9 minutes and 60 seconds. That is also 600 seconds.
#   The finger moves to 0 (with cost 2), pushes 0 (with cost 1), moves to 9
# (with cost 2), pushes 9 (with cost 1), moves to 6 (with cost 2), pushes 6
# (with cost 1), moves to 0 (with cost 2), and pushes 0 (with cost 1).
#   The cost is: 2 + 1 + 2 + 1 + 2 + 1 + 2 + 1 = 12.
# - 9 6 0, normalized as 0960 and interpreted as 9 minutes and 60 seconds.
#   The finger moves to 9 (with cost 2), pushes 9 (with cost 1), moves to 6
# (with cost 2), pushes 6 (with cost 1), moves to 0 (with cost 2), and pushes 0
# (with cost 1).
#   The cost is: 2 + 1 + 2 + 1 + 2 + 1 = 9.
#
# Example 2:
#
# Input: startAt = 0, moveCost = 1, pushCost = 2, targetSeconds = 76
# Output: 6
# Explanation: The optimal way is to push two digits: 7 6, interpreted as 76
# seconds.
# The finger moves to 7 (with cost 1), pushes 7 (with cost 2), moves to 6 (with
# cost 1), and pushes 6 (with cost 2). The total cost is: 1 + 2 + 1 + 2 = 6
# Note other possible ways are 0076, 076, 0116, and 116, but none of them
# produces the minimum cost.
#
#
#
# Constraints:
#
#
# 0 <= startAt <= 9
#
#
# 1 <= moveCost, pushCost <= 10^5
#
#
# 1 <= targetSeconds <= 6039
#

# @lc code=start
class Solution:
    def minCostSetTime(self, startAt: int, moveCost: int, pushCost: int, targetSeconds: int) -> int:
        """
        Interview explanation:
        Microwave mm:ss via digits 0-9. Move finger costs moveCost; push costs
        pushCost. Start finger on startAt. targetSeconds may be entered as
        minutes:seconds with seconds < 60, or equivalent forms (e.g. 1:99 invalid;
        but 99 seconds as 1:39 or 0:99 — only valid if seconds part < 100 and
        minutes < 100). Minimize cost among valid representations.

        Algorithm:
        (enumerate forms)
        - For mins in 0..99, secs = target - 60*mins; if 0<=secs<=99, form digit
          string of mins*100+secs without leading zeros (empty→"0"); compute cost
          of typing from startAt.

        Complexity: O(1) candidates (~100), O(1) space.
        """
        def cost(seq: str) -> int:
            cur = startAt
            total = 0
            for ch in seq:
                d = ord(ch) - 48
                if d != cur:
                    total += moveCost
                    cur = d
                total += pushCost
            return total

        ans = float("inf")
        for mins in range(100):
            secs = targetSeconds - 60 * mins
            if 0 <= secs <= 99:
                val = mins * 100 + secs
                seq = str(val) if val > 0 else "0"
                ans = min(ans, cost(seq))
        return int(ans)
# @lc code=end
