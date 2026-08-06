#
# @lc app=leetcode id=3374 lang=python3
#
# [3374] First Letter Capitalization II
#
# https://leetcode.com/problems/first-letter-capitalization-ii/description/
#
# database
# Hard (41.12%)
# Likes:    35
# Dislikes: 21
# Total Accepted:    10.9K
# Total Submissions: 26.4K
# Testcase Example:  "{\"headers\":{\"user_content\":[\"content_id\",\"content_text\"]},\"rows\":{\"user_content\":[[1,\"hello world of SQL\"],[2,\"the QUICK-brown fox\"],[3,\"modern-day DATA science\"],[4,\"web-based FRONT-end development\"]]}}"
#
#
# Table: user_content
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | content_id  | int     |
# | content_text| varchar |
# +-------------+---------+
# content_id is the unique key for this table.
# Each row contains a unique ID and the corresponding text content.
#
# Write a solution to transform the text in the content_text column by
# applying the following rules:
#
# Convert the first letter of each word to uppercase and the remaining
# letters to lowercase
#
# Special handling for words containing special characters:
#
# For words connected with a hyphen -, both parts should be capitalized
# (e.g., top-rated → Top-Rated)
#
# All other formatting and spacing should remain unchanged
#
# Return the result table that includes both the original content_text and
# the modified text following the above rules.
#
# The result format is in the following example.
#
# Example:
#
# Input:
#
# user_content table:
#
# +------------+---------------------------------+
# | content_id | content_text                    |
# +------------+---------------------------------+
# | 1          | hello world of SQL              |
# | 2          | the QUICK-brown fox             |
# | 3          | modern-day DATA science         |
# | 4          | web-based FRONT-end development |
# +------------+---------------------------------+
#
# Output:
#
# +------------+---------------------------------+---------------------------------+
# | content_id | original_text                   | converted_text
# |
# +------------+---------------------------------+---------------------------------+
# | 1          | hello world of SQL              | Hello World Of Sql
# |
# | 2          | the QUICK-brown fox             | The Quick-Brown Fox
# |
# | 3          | modern-day DATA science         | Modern-Day Data Science
# |
# | 4          | web-based FRONT-end development | Web-Based Front-End
# Development |
# +------------+---------------------------------+---------------------------------+
#
# Explanation:
#
# For content_id = 1:
#
# Each word's first letter is capitalized: "Hello World Of Sql"
#
# For content_id = 2:
#
# Contains the hyphenated word "QUICK-brown" which becomes "Quick-Brown"
#
# Other words follow normal capitalization rules
#
# For content_id = 3:
#
# Hyphenated word "modern-day" becomes "Modern-Day"
#
# "DATA" is converted to "Data"
#
# For content_id = 4:
#
# Contains two hyphenated words: "web-based" → "Web-Based"
#
# And "FRONT-end" → "Front-End"
#
# Constraints:
#
# context_text contains only English letters, and the characters in the
# list ['\', ' ', '@', '-', '/', '^', ',']
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Title-case words; hyphenated tokens capitalize each side (a-b -> A-B).

        Algorithm:
        - Recursive CTE split on spaces; for words with '-', title-case both parts.
        - GROUP_CONCAT in order.

        Complexity: O(N * L).
        """
        self.sql = """
WITH RECURSIVE Words AS (
    SELECT
        content_id,
        SUBSTRING_INDEX(content_text, ' ', 1) AS word,
        SUBSTRING(
            content_text,
            LENGTH(SUBSTRING_INDEX(content_text, ' ', 1)) + 2
        ) AS remaining_text,
        1 AS token_index
    FROM user_content
    UNION ALL
    SELECT
        content_id,
        SUBSTRING_INDEX(remaining_text, ' ', 1) AS word,
        SUBSTRING(
            remaining_text,
            LENGTH(SUBSTRING_INDEX(remaining_text, ' ', 1)) + 2
        ) AS remaining_text,
        token_index + 1 AS token_index
    FROM Words
    WHERE remaining_text != ''
),
Converted AS (
    SELECT
        content_id,
        GROUP_CONCAT(
            IF(
                word LIKE '%-%',
                CONCAT(
                    UPPER(SUBSTRING(word, 1, 1)),
                    LOWER(SUBSTRING(word, 2, LOCATE('-', word) - 2)),
                    '-',
                    UPPER(SUBSTRING(SUBSTRING_INDEX(word, '-', -1), 1, 1)),
                    LOWER(SUBSTRING(SUBSTRING_INDEX(word, '-', -1), 2))
                ),
                CONCAT(
                    UPPER(SUBSTRING(word, 1, 1)),
                    LOWER(SUBSTRING(word, 2))
                )
            )
            ORDER BY token_index SEPARATOR ' '
        ) AS converted_text
    FROM Words
    GROUP BY 1
)
SELECT
    u.content_id,
    u.content_text AS original_text,
    c.converted_text
FROM user_content AS u
INNER JOIN Converted AS c USING (content_id);
"""
        return self.sql
# @lc code=end
