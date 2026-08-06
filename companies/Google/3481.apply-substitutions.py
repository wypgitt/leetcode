#
# @lc app=leetcode id=3481 lang=python3
#
# [3481] Apply Substitutions
#
# https://leetcode.com/problems/apply-substitutions/description/
#
# algorithms
# Medium (77.94%)
# Likes:    63
# Dislikes: 5
# Total Accepted:    17K
# Total Submissions: 21.7K
# Testcase Example:  "[[\"A\",\"abc\"],[\"B\",\"def\"]]\n\"%A%_%B%\""
#
#
# You are given a replacements mapping and a text string that may contain
# placeholders formatted as %var%, where each var corresponds to a key in
# the replacements mapping. Each replacement value may itself contain one
# or more such placeholders. Each placeholder is replaced by the value
# associated with its corresponding replacement key.
#
# Return the fully substituted text string which does not contain any
# placeholders.
#
# Example 1:
#
# Input: replacements = [["A","abc"],["B","def"]], text = "%A%_%B%"
#
# Output: "abc_def"
#
# Explanation:
#
# The mapping associates "A" with "abc" and "B" with "def".
#
# Replace %A% with "abc" and %B% with "def" in the text.
#
# The final text becomes "abc_def".
#
# Example 2:
#
# Input: replacements = [["A","bce"],["B","ace"],["C","abc%B%"]], text =
# "%A%_%B%_%C%"
#
# Output: "bce_ace_abcace"
#
# Explanation:
#
# The mapping associates "A" with "bce", "B" with "ace", and "C" with
# "abc%B%".
#
# Replace %A% with "bce" and %B% with "ace" in the text.
#
# Then, for %C%, substitute %B% in "abc%B%" with "ace" to obtain "abcace".
#
# The final text becomes "bce_ace_abcace".
#
# Constraints:
#
# 1 <= replacements.length <= 10
#
# Each element of replacements is a two-element list [key, value], where:
#
# key is a single uppercase English letter.
#
# value is a non-empty string of at most 8 characters that may contain
# zero or more placeholders formatted as %<key>%.
#
# All replacement keys are unique.
#
# The text string is formed by concatenating all key placeholders
# (formatted as %<key>%) randomly from the replacements mapping, separated
# by underscores.
#
# text.length == 4 * replacements.length - 1
#
# Every placeholder in the text or in any replacement value corresponds to
# a key in the replacements mapping.
#
# There are no cyclic dependencies between replacement keys.
#

# @lc code=start
from typing import List
import re


class Solution:
    def applySubstitutions(self, replacements: List[List[str]], text: str) -> str:
        """
        Interview explanation:
        Placeholders %key% may nest in replacement values; the mapping is a DAG
        (no cycles). Fully expand each key once, then expand the text.

        Algorithm:
        - Build key -> value map.
        - Memoized resolve: scan for %key% and recurse into mapped values.
        - Apply the same resolver to text.

        Complexity: O(total expanded length) time/space (tiny under constraints).
        """
        mp = {k: v for k, v in replacements}
        memo = {}

        def resolve(s: str) -> str:
            if s in memo:
                return memo[s]
            parts = []
            i = 0
            while i < len(s):
                if s[i] == '%':
                    j = s.index('%', i + 1)
                    key = s[i + 1:j]
                    parts.append(resolve(mp[key]))
                    i = j + 1
                else:
                    parts.append(s[i])
                    i += 1
            memo[s] = ''.join(parts)
            return memo[s]

        return resolve(text)

    def applySubstitutions_regex(self, replacements: List[List[str]], text: str) -> str:
        """
        Interview explanation:
        Alternate: repeatedly substitute %X% until no placeholders remain
        (safe because the dependency graph is acyclic).

        Algorithm:
        - Expand all map values, then expand text via regex substitution.

        Complexity: O(passes * |text|) with tiny bounds.
        """
        mp = {k: v for k, v in replacements}
        pat = re.compile(r'%([A-Z])%')

        def expand(s: str) -> str:
            while '%' in s:
                s = pat.sub(lambda m: mp[m.group(1)], s)
            return s

        mp = {k: expand(v) for k, v in mp.items()}
        return expand(text)
# @lc code=end
