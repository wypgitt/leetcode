#
# @lc app=leetcode id=1410 lang=python3
#
# [1410] HTML Entity Parser
#
# https://leetcode.com/problems/html-entity-parser/description/
#
# algorithms
# Medium (50.02%)
# Likes:    218
# Dislikes: 333
# Total Accepted:    32.7K
# Total Submissions: 65.3K
# Testcase Example:  "\"&amp; is an HTML entity but &ambassador; is not.\""
#
# HTML entity parser is the parser that takes HTML code as input and replace
# all the entities of the special characters by the characters itself.
#
# The special characters and their entities for HTML are:
#
# Quotation Mark: the entity is " and symbol character is ".
#
# Single Quote Mark: the entity is ' and symbol character is '.
#
# Ampersand: the entity is & and symbol character is &.
#
# Greater Than Sign: the entity is > and symbol character is >.
#
# Less Than Sign: the entity is < and symbol character is <.
#
# Slash: the entity is ⁄ and symbol character is /.
#
# Given the input text string to the HTML parser, you have to implement the
# entity parser.
#
# Return the text after replacing the entities by the special characters.
#
# Example 1:
#
# Input: text = "& is an HTML entity but &ambassador; is not."
# Output: "& is an HTML entity but &ambassador; is not."
# Explanation: The parser will replace the & entity by &
#
# Example 2:
#
# Input: text = "and I quote: "...""
# Output: "and I quote: \"...\""
#
# Constraints:
#
# 1 <= text.length <= 10^5
#
# The string may contain any possible characters out of all the 256 ASCII
# characters.
#

# @lc code=start
class Solution:
    def entityParser(self, text: str) -> str:
        """
        Interview explanation:
        Replace HTML entities &quot; &apos; &amp; &gt; &lt; &frasl; with chars.
        Replace &amp; last (or scan carefully) so we do not double-replace.

        Algorithm:
        (dict scan)
        - Map entities→chars; scan text; if '&' try match known entity else emit '&'.

        Complexity: O(n) time, O(n) space for output.
        """
        mp = {
            "&quot;": '"',
            "&apos;": "'",
            "&amp;": "&",
            "&gt;": ">",
            "&lt;": "<",
            "&frasl;": "/",
        }
        res = []
        i, n = 0, len(text)
        while i < n:
            if text[i] == "&":
                matched = False
                for ent, ch in mp.items():
                    if text.startswith(ent, i):
                        res.append(ch)
                        i += len(ent)
                        matched = True
                        break
                if not matched:
                    res.append("&")
                    i += 1
            else:
                res.append(text[i])
                i += 1
        return "".join(res)

    def entityParser_replace(self, text: str) -> str:
        """
        Interview explanation:
        Alternate: successive str.replace; replace &amp; last to avoid creating
        new entities from partial replacements incorrectly — actually replace
        longer entities first, &amp; last.

        Algorithm:
        - For each entity except &amp;, replace; finally replace &amp;.

        Complexity: O(n * |entities|) time.
        """
        for ent, ch in [
            ("&quot;", '"'),
            ("&apos;", "'"),
            ("&gt;", ">"),
            ("&lt;", "<"),
            ("&frasl;", "/"),
            ("&amp;", "&"),
        ]:
            text = text.replace(ent, ch)
        return text
# @lc code=end
