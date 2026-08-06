#
# @lc app=leetcode id=2296 lang=python3
#
# [2296] Design a Text Editor
#
# https://leetcode.com/problems/design-a-text-editor/description/
#
# algorithms
# Hard (51.31%)
# Likes:    664
# Dislikes: 229
# Total Accepted:    45.9K
# Total Submissions: 89.5K
# Testcase Example:  "[\"TextEditor\",\"addText\",\"deleteText\",\"addText\",\"cursorRight\",\"cursorLeft\",\"deleteText\",\"cursorLeft\",\"cursorRight\"]\n[[],[\"leetcode\"],[4],[\"practice\"],[3],[8],[10],[2],[6]]"
#
# Design a text editor with a cursor that can do the following:
#
#
# Add text to where the cursor is.
#
#
# Delete text from where the cursor is (simulating the backspace key).
#
#
# Move the cursor either left or right.
#
# When deleting text, only characters to the left of the cursor will be deleted.
# The cursor will also remain within the actual text and cannot be moved beyond
# it. More formally, we have that 0 <= cursor.position <= currentText.length
# always holds.
#
# Implement the TextEditor class:
#
#
# TextEditor() Initializes the object with empty text.
#
#
# void addText(string text) Appends text to where the cursor is. The cursor ends
# to the right of text.
#
#
# int deleteText(int k) Deletes k characters to the left of the cursor. Returns
# the number of characters actually deleted.
#
#
# string cursorLeft(int k) Moves the cursor to the left k times. Returns the
# last min(10, len) characters to the left of the cursor, where len is the
# number of characters to the left of the cursor.
#
#
# string cursorRight(int k) Moves the cursor to the right k times. Returns the
# last min(10, len) characters to the left of the cursor, where len is the
# number of characters to the left of the cursor.
#
#
#
# Example 1:
#
# Input
# ["TextEditor", "addText", "deleteText", "addText", "cursorRight",
# "cursorLeft", "deleteText", "cursorLeft", "cursorRight"]
# [[], ["leetcode"], [4], ["practice"], [3], [8], [10], [2], [6]]
# Output
# [null, null, 4, null, "etpractice", "leet", 4, "", "practi"]
#
# Explanation
# TextEditor textEditor = new TextEditor(); // The current text is "|". (The '|'
# character represents the cursor)
# textEditor.addText("leetcode"); // The current text is "leetcode|".
# textEditor.deleteText(4); // return 4
#                           // The current text is "leet|".
#                           // 4 characters were deleted.
# textEditor.addText("practice"); // The current text is "leetpractice|".
# textEditor.cursorRight(3); // return "etpractice"
#                            // The current text is "leetpractice|".
#                            // The cursor cannot be moved beyond the actual
# text and thus did not move.
#                            // "etpractice" is the last 10 characters to the
# left of the cursor.
# textEditor.cursorLeft(8); // return "leet"
#                           // The current text is "leet|practice".
#                           // "leet" is the last min(10, 4) = 4 characters to
# the left of the cursor.
# textEditor.deleteText(10); // return 4
#                            // The current text is "|practice".
#                            // Only 4 characters were deleted.
# textEditor.cursorLeft(2); // return ""
#                           // The current text is "|practice".
#                           // The cursor cannot be moved beyond the actual text
# and thus did not move.
#                           // "" is the last min(10, 0) = 0 characters to the
# left of the cursor.
# textEditor.cursorRight(6); // return "practi"
#                            // The current text is "practi|ce".
#                            // "practi" is the last min(10, 6) = 6 characters
# to the left of the cursor.
#
#
#
# Constraints:
#
#
# 1 <= text.length, k <= 40
#
#
# text consists of lowercase English letters.
#
#
# At most 2 * 10^4 calls in total will be made to addText, deleteText,
# cursorLeft and cursorRight.
#
#
#
# Follow-up: Could you find a solution with time complexity of O(k) per call?
#

# @lc code=start
class TextEditor:
    def __init__(self):
        """
        Interview explanation:
        Text editor with cursor: add/delete left of cursor; move cursor;
        return up to 10 chars left of cursor after moves.

        Algorithm:
        - Two stacks (left of cursor / right of cursor) for O(k) ops.

        Complexity: O(total text) space.
        """
        self.left: list = []
        self.right: list = []

    def addText(self, text: str) -> None:
        """
        Interview explanation:
        Insert text at cursor (to the left stack).

        Algorithm:
        - Extend left with characters.

        Complexity: O(|text|).
        """
        self.left.extend(text)

    def deleteText(self, k: int) -> int:
        """
        Interview explanation:
        Delete up to k chars left of cursor; return #deleted.

        Algorithm:
        - Pop min(k, len(left)) from left.

        Complexity: O(k).
        """
        k = min(k, len(self.left))
        del self.left[-k:]
        return k

    def cursorLeft(self, k: int) -> str:
        """
        Interview explanation:
        Move cursor left k (or to start); return last min(10, left) chars.

        Algorithm:
        - Move chars from left to right.

        Complexity: O(k).
        """
        k = min(k, len(self.left))
        for _ in range(k):
            self.right.append(self.left.pop())
        return "".join(self.left[-10:])

    def cursorRight(self, k: int) -> str:
        """
        Interview explanation:
        Move cursor right k (or to end); return last min(10, left) chars.

        Algorithm:
        - Move chars from right to left.

        Complexity: O(k).
        """
        k = min(k, len(self.right))
        for _ in range(k):
            self.left.append(self.right.pop())
        return "".join(self.left[-10:])


# Your TextEditor object will be instantiated and called as such:
# obj = TextEditor()
# obj.addText(text)
# param_2 = obj.deleteText(k)
# param_3 = obj.cursorLeft(k)
# param_4 = obj.cursorRight(k)
# @lc code=end
