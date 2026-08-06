#
# @lc app=leetcode id=3368 lang=python3
#
# [3368] First Letter Capitalization
#
# https://leetcode.com/problems/first-letter-capitalization/description/
#
# database
# Hard (86.44%)
# Likes:    6
# Dislikes: 1
# Total Accepted:    1.4K
# Total Submissions: 1.6K
# Testcase Example:  "{\"headers\":{\"user_content\":[\"content_id\",\"content_text\"]},\"rows\":{\"user_content\":[[1,\"hello world of SQL\"],[2,\"the QUICK brown fox\"],[3,\"data science AND machine learning\"],[4,\"TOP rated programming BOOKS\"]]}}"
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
# Convert the first letter of each word to uppercase
#
# Keep all other letters in lowercase
#
# Preserve all existing spaces
#
# Note: There will be no special character in content_text.
#
# Return the result table that includes both the original content_text and
# the modified text where each word starts with a capital letter.
#
# The result format is in the following example.
#
# Example:
#
# Input:
#
# user_content table:
#
# +------------+-----------------------------------+
# | content_id | content_text                      |
# +------------+-----------------------------------+
# | 1          | hello world of SQL                |
# | 2          | the QUICK brown fox               |
# | 3          | data science AND machine learning |
# | 4          | TOP rated programming BOOKS       |
# +------------+-----------------------------------+
#
# Output:
#
# +------------+-----------------------------------+-----------------------------------+
# | content_id | original_text                     | converted_text
# |
# +------------+-----------------------------------+-----------------------------------+
# | 1          | hello world of SQL                | Hello World Of Sql
# |
# | 2          | the QUICK brown fox               | The Quick Brown Fox
# |
# | 3          | data science AND machine learning | Data Science And
# Machine Learning |
# | 4          | TOP rated programming BOOKS       | Top Rated Programming
# Books       |
# +------------+-----------------------------------+-----------------------------------+
#
# Explanation:
#
# For content_id = 1:
#
# Each word's first letter is capitalized: Hello World Of Sql
#
# For content_id = 2:
#
# Original mixed-case text is transformed to title case: The Quick Brown
# Fox
#
# For content_id = 3:
#
# The word AND is converted to "And": "Data Science And Machine Learning"
#
# For content_id = 4:
#
# Handles word TOP rated correctly: Top Rated
#
# Converts BOOKS from all caps to title case: Books
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: title-case each space-separated word in content_text.
        Return content_id, original_text, converted_text.

        Algorithm:
        - Recursive CTE splits on spaces; UPPER(first) + LOWER(rest) per word.
        - GROUP_CONCAT back in token order.

        Complexity: O(N * L) in words/length.
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
            CONCAT(UPPER(SUBSTRING(word, 1, 1)), LOWER(SUBSTRING(word, 2)))
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
