#
# @lc app=leetcode id=3052 lang=python3
#
# [3052] Maximize Items
#
# https://leetcode.com/problems/maximize-items/description/
#
# database
# Hard (74.50%)
# Likes:    7
# Dislikes: 12
# Total Accepted:    2.2K
# Total Submissions: 2.9K
# Testcase Example:  "{\"headers\":{\"Inventory\":[\"item_id\",\"item_type\",\"item_category\",\"square_footage\"]},\"rows\":{\"Inventory\":[[1374,\"prime_eligible\",\"Watches\",68.00],[4245,\"not_prime\",\"Art\",26.40],[5743,\"prime_eligible\",\"Software\",325.00],[8543,\"not_prime\",\"Clothing\",64.50],[2556,\"not_prime\",\"Shoes\",15.00],[2452,\"prime_eligible\",\"Scientific\",85.00],[3255,\"not_prime\",\"Furniture\",22.60],[1672,\"prime_eligible\",\"Beauty\",8.50],[4256,\"prime_eligible\",\"Furniture\",55.50],[6325,\"prime_eligible\",\"Food\",13.20]]}}"
#
#
# Table: Inventory
#
# +----------------+---------+
# | Column Name    | Type    |
# +----------------+---------+
# | item_id        | int     |
# | item_type      | varchar |
# | item_category  | varchar |
# | square_footage | decimal |
# +----------------+---------+
# item_id is the column of unique values for this table.
# Each row includes item id, item type, item category and square footage.
#
# Leetcode warehouse wants to maximize the number of items it can stock in
# a 500,000 square feet warehouse. It wants to stock as many prime items as
# possible, and afterwards use the remaining square footage to stock the
# most number of non-prime items.
#
# Write a solution to find the number of prime and non-prime items that can
# be stored in the 500,000 square feet warehouse. Output the item type with
# prime_eligible followed by not_prime and the maximum number of items that
# can be stocked.
#
# Note:
#
# Item count must be a whole number (integer).
#
# If the count for the not_prime category is 0, you should output 0 for
# that particular category.
#
# Return the result table ordered by item count in descending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Inventory table:
# +---------+----------------+---------------+----------------+
# | item_id | item_type      | item_category | square_footage |
# +---------+----------------+---------------+----------------+
# | 1374    | prime_eligible | Watches       | 68.00          |
# | 4245    | not_prime      | Art           | 26.40          |
# | 5743    | prime_eligible | Software      | 325.00         |
# | 8543    | not_prime      | Clothing      | 64.50          |
# | 2556    | not_prime      | Shoes         | 15.00          |
# | 2452    | prime_eligible | Scientific    | 85.00          |
# | 3255    | not_prime      | Furniture     | 22.60          |
# | 1672    | prime_eligible | Beauty        | 8.50           |
# | 4256    | prime_eligible | Furniture     | 55.50          |
# | 6325    | prime_eligible | Food          | 13.20          |
# +---------+----------------+---------------+----------------+
# Output:
# +----------------+-------------+
# | item_type      | item_count  |
# +----------------+-------------+
# | prime_eligible | 5400        |
# | not_prime      | 8           |
# +----------------+-------------+
# Explanation:
# - The prime-eligible category comprises a total of 6 items, amounting to
# a combined square footage of 555.20. It is possible to store 900
# combinations of these 6 items, totaling 5400 items and occupying 499,680
# square footage.
# - In the not_prime category, there are a total of 4 items with a combined
# square footage of 128.50. After deducting prime storage (320 remaining),
# there is room for 2 combinations (8 non-prime items).
# Output table is ordered by item count in descending order.
#

# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Inventory(item_id, item_type, item_category, square_footage).
        Stock a 500,000 sq ft warehouse: maximize prime_eligible items by repeating
        the full prime set, then pack as many not_prime sets as fit in the leftover
        space. Return item_type and item_count ordered by item_count DESC.

        Algorithm:
        - SUM/COUNT square footage per item_type.
        - prime kits = FLOOR(500000 / prime_sq); rem after prime kits.
        - not_prime kits = FLOOR(rem / np_sq); counts = kits * type_count.
        - UNION both types (0 when a type is missing or no leftover room).

        Complexity: O(N).
        """
        self.sql = """
WITH summary AS (
    SELECT
        item_type,
        COUNT(*) AS cnt,
        SUM(square_footage) AS total_sq
    FROM Inventory
    GROUP BY item_type
),
metrics AS (
    SELECT
        IFNULL(
            (
                SELECT FLOOR(500000 / total_sq) * cnt
                FROM summary
                WHERE item_type = 'prime_eligible'
            ),
            0
        ) AS prime_count,
        IFNULL(
            (
                SELECT FLOOR(500000 / total_sq) * total_sq
                FROM summary
                WHERE item_type = 'prime_eligible'
            ),
            0
        ) AS prime_used,
        IFNULL(
            (SELECT cnt FROM summary WHERE item_type = 'not_prime'),
            0
        ) AS np_cnt,
        IFNULL(
            (SELECT total_sq FROM summary WHERE item_type = 'not_prime'),
            NULL
        ) AS np_sq
)
SELECT item_type, item_count
FROM (
    SELECT 'prime_eligible' AS item_type, prime_count AS item_count
    FROM metrics
    UNION ALL
    SELECT
        'not_prime',
        CASE
            WHEN np_sq IS NULL OR np_sq = 0 THEN 0
            ELSE FLOOR((500000 - prime_used) / np_sq) * np_cnt
        END
    FROM metrics
) AS t
ORDER BY item_count DESC;
"""
        return self.sql
# @lc code=end
