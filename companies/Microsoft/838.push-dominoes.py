#
# @lc app=leetcode id=838 lang=python3
#
# [838] Push Dominoes
#
# https://leetcode.com/problems/push-dominoes/description/
#
# algorithms
# Medium (63.05%)
# Likes:    3973
# Dislikes: 278
# Total Accepted:    232K
# Total Submissions: 368K
# Testcase Example:  "\"RR.L\""
#
# There are n dominoes in a line, and we place each domino vertically upright.
# In the beginning, we simultaneously push some of the dominoes either to the
# left or to the right.
#
# After each second, each domino that is falling to the left pushes the
# adjacent domino on the left. Similarly, the dominoes falling to the right
# push their adjacent dominoes standing on the right.
#
# When a vertical domino has dominoes falling on it from both sides, it stays
# still due to the balance of the forces.
#
# For the purposes of this question, we will consider that a falling domino
# expends no additional force to a falling or already fallen domino.
#
# You are given a string dominoes representing the initial state where:
#
# dominoes[i] = 'L', if the i^th domino has been pushed to the left,
#
# dominoes[i] = 'R', if the i^th domino has been pushed to the right, and
#
# dominoes[i] = '.', if the i^th domino has not been pushed.
#
# Return a string representing the final state.
#
# Example 1:
#
# Input: dominoes = "RR.L"
# Output: "RR.L"
# Explanation: The first domino expends no additional force on the second
# domino.
#
# Example 2:
#
# Input: dominoes = ".L.R...LR..L.."
# Output: "LL.RR.LLRRLL.."
#
# Constraints:
#
# n == dominoes.length
#
# 1 <= n <= 10^5
#
# dominoes[i] is either 'L', 'R', or '.'.
#

# @lc code=start

class Solution:
    def pushDominoes(self, dominoes: str) -> str:
        """
        Interview explanation:
        Forces from L and R propagate. Two-pass force magnitudes: rightward
        force from R decreasing, leftward from L decreasing; net sign decides
        final state. Classic force simulation.

        Algorithm:
        - forces[i]: + from R, - from L; compare and set R/L/. 

        Complexity: O(n) time, O(n) space.
        """
        n = len(dominoes)
        forces = [0] * n
        f = 0
        for i in range(n):
            if dominoes[i] == "R":
                f = n
            elif dominoes[i] == "L":
                f = 0
            else:
                f = max(f - 1, 0)
            forces[i] += f
        f = 0
        for i in range(n - 1, -1, -1):
            if dominoes[i] == "L":
                f = n
            elif dominoes[i] == "R":
                f = 0
            else:
                f = max(f - 1, 0)
            forces[i] -= f
        return "".join("R" if x > 0 else "L" if x < 0 else "." for x in forces)

    def pushDominoes_segments(self, dominoes: str) -> str:
        """
        Interview explanation:
        Segment approach: pad with L...R sentinels; between two fixed ends,
        fill based on (left,right) pair: same→all that; R..L→meet in middle;
        L..R→stay dots.

        Algorithm:
        - Find consecutive non-dot anchors; fill interval by case analysis.

        Complexity: O(n) time, O(n) space.
        """
        s = "L" + dominoes + "R"
        n = len(s)
        arr = list(s)
        i = 0
        for j in range(1, n):
            if s[j] == ".":
                continue
            if s[i] == s[j]:
                for k in range(i + 1, j):
                    arr[k] = s[i]
            elif s[i] == "R" and s[j] == "L":
                l, r = i + 1, j - 1
                while l < r:
                    arr[l] = "R"
                    arr[r] = "L"
                    l += 1
                    r -= 1
            i = j
        return "".join(arr[1:-1])
# @lc code=end
