#
# @lc app=leetcode id=3389 lang=python3
#
# [3389] Minimum Operations to Make Character Frequencies Equal
#
# https://leetcode.com/problems/minimum-operations-to-make-character-frequencies-equal/description/
#
# algorithms
# Hard (26.81%)
# Likes:    78
# Dislikes: 2
# Total Accepted:    4.9K
# Total Submissions: 18.4K
# Testcase Example:  "\"acab\""
#
#
# You are given a string s.
#
# A string t is called good if all characters of t occur the same number
# of times.
#
# You can perform the following operations any number of times:
#
# Delete a character from s.
#
# Insert a character in s.
#
# Change a character in s to its next letter in the alphabet.
#
# Note that you cannot change 'z' to 'a' using the third operation.
#
# Return the minimum number of operations required to make s good.
#
# Example 1:
#
# Input: s = "acab"
#
# Output: 1
#
# Explanation:
#
# We can make s good by deleting one occurrence of character 'a'.
#
# Example 2:
#
# Input: s = "wddw"
#
# Output: 0
#
# Explanation:
#
# We do not need to perform any operations since s is initially good.
#
# Example 3:
#
# Input: s = "aaabc"
#
# Output: 2
#
# Explanation:
#
# We can make s good by applying these operations:
#
# Change one occurrence of 'a' to 'b'
#
# Insert one occurrence of 'c' into s
#
# Constraints:
#
# 3 <= s.length <= 2 * 10^4
#
# s contains only lowercase English letters.
#

# @lc code=start

class Solution:
    def makeStringGood(self, s: str) -> int:
        """
        Interview explanation:
        A good string has one common frequency among present letters. Operations
        are delete, insert, or change c→next letter (no wrap). Try every target
        frequency and DP over the alphabet left-to-right/right-to-left, optionally
        cascading surplus into the next letter's deficit via changes.

        Algorithm:
        - count[0..25]; for target in 1..max(count):
          dp[i] = min ops for letters i..z to be absent or have frequency target.
        - Transitions: delete-all, insert/delete to target, or pair i with i+1 via
          changes when i+1 has a deficit.

        Complexity: O(26 * max_freq) = O(n) time, O(1) space.
        """
        count = [0] * 26
        for c in s:
            count[ord(c) - ord('a')] += 1
        return min(
            self._ops_for_target(count, target)
            for target in range(1, max(count) + 1)
        )

    def _ops_for_target(self, count: list[int], target: int) -> int:
        dp = [0] * 27
        for i in range(25, -1, -1):
            delete_all = count[i]
            to_target = abs(target - count[i])
            dp[i] = min(delete_all, to_target) + dp[i + 1]
            if i + 1 < 26 and count[i + 1] < target:
                next_deficit = target - count[i + 1]
                need = count[i] if count[i] <= target else count[i] - target
                change_cost = max(need, next_deficit)
                dp[i] = min(dp[i], change_cost + dp[i + 2])
        return dp[0]
# @lc code=end
