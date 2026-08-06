#
# @lc app=leetcode id=591 lang=python3
#
# [591] Tag Validator
#
# https://leetcode.com/problems/tag-validator/description/
#
# algorithms
# Hard (41.24%)
# Likes:    185
# Dislikes: 655
# Total Accepted:    22.5K
# Total Submissions: 54.5K
# Testcase Example:  "\"<DIV>This is the first line <![CDATA[<div>]]></DIV>\""
#
# Given a string representing a code snippet, implement a tag validator to
# parse the code and return whether it is valid.
#
# A code snippet is valid if all the following rules hold:
#
# The code must be wrapped in a valid closed tag. Otherwise, the code is
# invalid.
#
# A closed tag (not necessarily valid) has exactly the following format :
# <TAG_NAME>TAG_CONTENT</TAG_NAME>. Among them, <TAG_NAME> is the start tag,
# and </TAG_NAME> is the end tag. The TAG_NAME in start and end tags should be
# the same. A closed tag is valid if and only if the TAG_NAME and TAG_CONTENT
# are valid.
#
# A valid TAG_NAME only contain upper-case letters, and has length in range
# [1,9]. Otherwise, the TAG_NAME is invalid.
#
# A valid TAG_CONTENT may contain other valid closed tags, cdata and any
# characters (see note1) EXCEPT unmatched <, unmatched start and end tag, and
# unmatched or closed tags with invalid TAG_NAME. Otherwise, the TAG_CONTENT is
# invalid.
#
# A start tag is unmatched if no end tag exists with the same TAG_NAME, and
# vice versa. However, you also need to consider the issue of unbalanced when
# tags are nested.
#
# A < is unmatched if you cannot find a subsequent >. And when you find a < or
# </, all the subsequent characters until the next > should be parsed as
# TAG_NAME (not necessarily valid).
#
# The cdata has the following format : <![CDATA[CDATA_CONTENT]]>. The range of
# CDATA_CONTENT is defined as the characters between <![CDATA[ and the first
# subsequent ]]>.
#
# CDATA_CONTENT may contain any characters. The function of cdata is to forbid
# the validator to parse CDATA_CONTENT, so even it has some characters that can
# be parsed as tag (no matter valid or invalid), you should treat it as regular
# characters.
#
# Example 1:
#
# Input: code = "<DIV>This is the first line <![CDATA[<div>]]></DIV>"
# Output: true
# Explanation:
# The code is wrapped in a closed tag : <DIV> and </DIV>.
# The TAG_NAME is valid, the TAG_CONTENT consists of some characters and cdata.
# Although CDATA_CONTENT has an unmatched start tag with invalid TAG_NAME, it
# should be considered as plain text, not parsed as a tag.
# So TAG_CONTENT is valid, and then the code is valid. Thus return true.
#
# Example 2:
#
# Input: code = "<DIV>>> ![cdata[]] <![CDATA[<div>]>]]>]]>>]</DIV>"
# Output: true
# Explanation:
# We first separate the code into : start_tag|tag_content|end_tag.
# start_tag -> "<DIV>"
# end_tag -> "</DIV>"
# tag_content could also be separated into : text1|cdata|text2.
# text1 -> ">> ![cdata[]] "
# cdata -> "<![CDATA[<div>]>]]>", where the CDATA_CONTENT is "<div>]>"
# text2 -> "]]>>]"
# The reason why start_tag is NOT "<DIV>>>" is because of the rule 6.
# The reason why cdata is NOT "<![CDATA[<div>]>]]>]]>" is because of the rule
# 7.
#
# Example 3:
#
# Input: code = "<A> <B> </A> </B>"
# Output: false
# Explanation: Unbalanced. If "<A>" is closed, then "<B>" must be unmatched,
# and vice versa.
#
# Constraints:
#
# 1 <= code.length <= 500
#
# code consists of English letters, digits, '<', '>', '/', '!', '[', ']', '.',
# and ' '.
#



# @lc code=start
from typing import List


class Solution:
    def isValid(self, code: str) -> bool:
        """
        Interview explanation:
        Validate a nested HTML-like tag string: uppercase tag names length
        1..9, matching open/close stack, CDATA sections that skip validation,
        and the whole code wrapped in exactly one root tag pair.

        Algorithm:
        - Scan with index i; maintain a stack of open tag names.
        - On "<![CDATA[" … "]]>" skip content (only valid inside tags).
        - On "</TAG>" pop and match; on "<TAG>" push if valid name.
        - Plain text only allowed inside an open tag; nothing after root closes.
        - Success when the scan finishes with an empty stack after a closed root.

        Complexity: O(n) time, O(n) stack space.
        """
        if not code:
            return False
        stack: List[str] = []
        i, n = 0, len(code)

        def is_valid_name(name: str) -> bool:
            return 1 <= len(name) <= 9 and name.isalpha() and name.isupper()

        while i < n:
            if not stack and i > 0:
                return False
            if code.startswith("<![CDATA[", i):
                if not stack:
                    return False
                j = code.find("]]>", i + 9)
                if j < 0:
                    return False
                i = j + 3
            elif code.startswith("</", i):
                j = code.find(">", i + 2)
                if j < 0:
                    return False
                name = code[i + 2:j]
                if not stack or stack[-1] != name or not is_valid_name(name):
                    return False
                stack.pop()
                i = j + 1
                if not stack and i < n:
                    return False
            elif code.startswith("<", i):
                j = code.find(">", i + 1)
                if j < 0:
                    return False
                name = code[i + 1:j]
                if not is_valid_name(name):
                    return False
                stack.append(name)
                i = j + 1
            else:
                if not stack:
                    return False
                i += 1
        return not stack
# @lc code=end


