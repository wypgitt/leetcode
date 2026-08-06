#
# @lc app=leetcode id=3995 lang=python3
#
# [3995] Minimum Cost to Convert String III
#
# https://leetcode.com/problems/minimum-cost-to-convert-string-iii/description/
#
# algorithms
# Hard (55.18%)
# Likes:    28
# Dislikes: 3
# Total Accepted:    6.6K
# Total Submissions: 12K
# Testcase Example:  "\"hello\"\n\"world\"\n[[\"he\",\"wo\"],[\"llo\",\"rld\"]]\n[3,4]"
#
#
# You are given two strings, source and target.
#
# You are also given a 2D string array rules, where rules[i] = [pattern_i,
# replacement_i], and an integer array costs, where costs[i] is the base
# cost of applying rules[i]. Both arrays have the same length.
# Additionally, pattern_i and replacement_i have the same length.
#
# You may apply any rule any number of times. Each rule application works
# as follows:
#
# Choose an index l such that the range of positions from l to l +
# pattern_i.length - 1 exists in the current string and none of these
# positions has been used in a previous rule application.
#
# For each index j, the character pattern_i[j] must either be equal to the
# current character at position l + j, or be '*'.
#
# Replace the characters in this range with replacement_i. The replacement
# is used exactly as given and does not contain wildcards.
#
# The cost of this rule application is costs[i] plus the number of '*'
# characters in pattern_i.
#
# Once a character position has been used in a rule application, it cannot
# be used in any later rule application.
#
# Since every pattern_i and replacement_i have the same length, character
# positions are preserved after every rule application.
#
# Return the minimum total cost required to transform source into target.
# If it is impossible, return -1.
#
# Example 1:
#
# Input: source = "hello", target = "world", rules =
# [["he","wo"],["llo","rld"]], costs = [3,4]
#
# Output: 7
#
# Explanation:
#
# Apply rules[0] to replace "he" with "wo" at cost 3, so the string
# becomes "wollo".
#
# Apply rules[1] to replace "llo" with "rld" at cost 4, so the string
# becomes "world".
#
# The total cost is 3 + 4 = 7.
#
# Example 2:
#
# Input: source = "cat", target = "dog", rules = [["c*t","dog"]], costs =
# [2]
#
# Output: 3
#
# Explanation:
#
# Apply rules[0] to replace "cat" with "dog". The wildcard '*' matches
# 'a', adding 1 to the base cost 2.
#
# The total cost is 2 + 1 = 3.
#
# Example 3:
#
# Input: source = "test", target = "next", rules = [["*e*t","next"]],
# costs = [4]
#
# Output: 6
#
# Explanation:
#
# Apply rules[0] to replace "test" with "next". The first wildcard matches
# 't' and the second wildcard matches 's', adding 2 to the base cost 4.
#
# The total cost is 4 + 2 = 6.
#
# Example 4:
#
# Input: source = "ab", target = "bc", rules = [["a*","bd"]], costs = [9]
#
# Output: -1
#
# Explanation:
#
# No sequence of rule applications can transform source into target, so
# the answer is -1.
#
# Constraints:
#
# 1 <= source.length == target.length <= 5000
#
# source and target consist of lowercase English letters.
#
# 1 <= rules.length == costs.length <= 200
#
# rules[i] = [pattern_i, replacement_i]
#
# 1 <= pattern_i.length == replacement_i.length <= 20
#
# pattern_i contains at least one lowercase English letter and at most 5
# '*' characters.
#
# replacement_i contains only lowercase English letters.
#
# 1 <= costs[i] <= 1000
#

# @lc code=start
class Solution:
    def minCost(
        self,
        source: str,
        target: str,
        rules: list[list[str]],
        costs: list[int],
    ) -> int:
        """
        Interview explanation:
        Non-overlapping pattern applications turn source into target. Positions
        that already match may be skipped; mismatches must be covered. DP over
        prefixes tries skip (if equal) or each rule starting here.

        Algorithm:
        - dp[i] = min cost to finish source[:i] -> target[:i].
        - From i: if source[i]==target[i], dp[i+1] = min(..., dp[i]).
        - For each rule (pattern, replacement) matching source[i:] with
          wildcards and equaling target on the span, update dp[i+L] with
          costs[j] + (# of '*').

        Complexity: O(n * R * L) time with L <= 20, O(n) space.
        """
        n = len(source)
        INF = 10**18
        dp = [INF] * (n + 1)
        dp[0] = 0
        prepared = []
        for (pat, rep), base in zip(rules, costs):
            prepared.append((pat, rep, base + pat.count("*")))

        for i in range(n):
            if dp[i] >= INF:
                continue
            if source[i] == target[i]:
                if dp[i] < dp[i + 1]:
                    dp[i + 1] = dp[i]
            for pat, rep, cost in prepared:
                L = len(pat)
                if i + L > n:
                    continue
                ok = True
                for j in range(L):
                    pc = pat[j]
                    if pc != "*" and pc != source[i + j]:
                        ok = False
                        break
                    if rep[j] != target[i + j]:
                        ok = False
                        break
                if ok and dp[i] + cost < dp[i + L]:
                    dp[i + L] = dp[i] + cost
        return -1 if dp[n] >= INF else dp[n]
# @lc code=end
