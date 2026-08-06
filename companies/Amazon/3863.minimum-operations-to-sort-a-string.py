#
# @lc app=leetcode id=3863 lang=python3
#
# [3863] Minimum Operations to Sort a String
#
# https://leetcode.com/problems/minimum-operations-to-sort-a-string/description/
#
# algorithms
# Medium (19.34%)
# Likes:    101
# Dislikes: 10
# Total Accepted:    18.1K
# Total Submissions: 93.6K
# Testcase Example:  "\"dog\""
#
#
# You are given a string s consisting of lowercase English letters.
#
# In one operation, you can select any substring of s that is not the
# entire string and sort it in non-descending alphabetical order.
#
# Return the minimum number of operations required to make s sorted in
# non-descending order. If it is not possible, return -1.
#
# Example 1:
#
# Input: s = "dog"
#
# Output: 1
#
# Explanation:​​​​​​​
#
# Sort substring "og" to "go".
#
# Now, s = "dgo", which is sorted in ascending order. Thus, the answer is
# 1.
#
# Example 2:
#
# Input: s = "card"
#
# Output: 2
#
# Explanation:
#
# Sort substring "car" to "acr", so s = "acrd".
#
# Sort substring "rd" to "dr", making s = "acdr", which is sorted in
# ascending order. Thus, the answer is 2.
#
# Example 3:
#
# Input: s = "gf"
#
# Output: -1
#
# Explanation:
#
# It is impossible to sort s under the given constraints. Thus, the answer
# is -1.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists of only lowercase English letters.
#

# @lc code=start
class Solution:
    def minOperations(self, s: str) -> int:
        """
        Interview explanation:
        Sorting a proper substring can place global min at front or global max
        at back; casework on where min/max sit gives the min ops (or -1).

        Algorithm:
        - Already sorted → 0; length 2 unsorted → -1.
        - If s[0] is global min or s[-1] is global max → 1.
        - Else if some middle char is global min or max → 2.
        - Else min is only at the end and max only at the start → 3.

        Complexity: O(n) time, O(1) space.
        """
        n = len(s)
        if all(s[i] <= s[i + 1] for i in range(n - 1)):
            return 0
        if n == 2:
            return -1
        mn, mx = min(s), max(s)
        if s[0] == mn or s[-1] == mx:
            return 1
        if any(c == mn or c == mx for c in s[1:-1]):
            return 2
        return 3
# @lc code=end
