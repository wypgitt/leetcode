#
# @lc app=leetcode id=1990 lang=python3
#
# [1990] Count the Number of Experiments
#
# https://leetcode.com/problems/count-the-number-of-experiments/description/
#
# database
# Medium (48.91%)
# Likes:    27
# Dislikes: 203
# Total Accepted:    10.2K
# Total Submissions: 20.8K
# Testcase Example:  "{\"headers\":{\"Experiments\":[\"experiment_id\",\"platform\",\"experiment_name\"]},\"rows\":{\"Experiments\":[[4,\"IOS\",\"Programming\"],[13,\"IOS\",\"Sports\"],[14,\"Android\",\"Reading\"],[8,\"Web\",\"Reading\"],[12,\"Web\",\"Reading\"],[18,\"Web\",\"Programming\"]]}}"
#
#
# Table: Experiments
#
# +-----------------+------+
# | Column Name     | Type |
# +-----------------+------+
# | experiment_id   | int  |
# | platform        | enum |
# | experiment_name | enum |
# +-----------------+------+
# experiment_id is the column with unique values for this table.
# platform is an enum (category) type of values ('Android', 'IOS', 'Web').
# experiment_name is an enum (category) type of values ('Reading',
# 'Sports', 'Programming').
# This table contains information about the ID of an experiment done with
# a random person, the platform used to do the experiment, and the name of
# the experiment.
#
# Write a solution to report the number of experiments done on each of the
# three platforms for each of the three given experiments. Notice that all
# the pairs of (platform, experiment) should be included in the output
# including the pairs with zero experiments.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Experiments table:
# +---------------+----------+-----------------+
# | experiment_id | platform | experiment_name |
# +---------------+----------+-----------------+
# | 4             | IOS      | Programming     |
# | 13            | IOS      | Sports          |
# | 14            | Android  | Reading         |
# | 8             | Web      | Reading         |
# | 12            | Web      | Reading         |
# | 18            | Web      | Programming     |
# +---------------+----------+-----------------+
# Output:
# +----------+-----------------+-----------------+
# | platform | experiment_name | num_experiments |
# +----------+-----------------+-----------------+
# | Android  | Reading         | 1               |
# | Android  | Sports          | 0               |
# | Android  | Programming     | 0               |
# | IOS      | Reading         | 0               |
# | IOS      | Sports          | 1               |
# | IOS      | Programming     | 1               |
# | Web      | Reading         | 2               |
# | Web      | Sports          | 0               |
# | Web      | Programming     | 1               |
# +----------+-----------------+-----------------+
# Explanation:
# On the platform "Android", we had only one "Reading" experiment.
# On the platform "IOS", we had one "Sports" experiment and one
# "Programming" experiment.
# On the platform "Web", we had two "Reading" experiments and one
# "Programming" experiment.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Platforms {Android,IOS,Web} × experiment names
        {Reading,Sports,Programming} form 9 pairs. Count how many experiments
        exist for each pair (0 if none).

        Algorithm:
        - Cross join distinct platforms and names; LEFT JOIN Experiments; COUNT.

        Complexity: O(E) aggregation.
        """
        return self.sql

    sql = """
    WITH platforms AS (
        SELECT 'Android' AS platform
        UNION ALL SELECT 'IOS'
        UNION ALL SELECT 'Web'
    ),
    names AS (
        SELECT 'Reading' AS experiment_name
        UNION ALL SELECT 'Sports'
        UNION ALL SELECT 'Programming'
    )
    SELECT p.platform, n.experiment_name,
           COUNT(e.experiment_id) AS num_experiments
    FROM platforms p
    CROSS JOIN names n
    LEFT JOIN Experiments e
      ON e.platform = p.platform AND e.experiment_name = n.experiment_name
    GROUP BY p.platform, n.experiment_name;
    """

    def solve_values(self) -> str:
        """
        Interview explanation:
        Alternate: VALUES lists for platforms/names then same LEFT JOIN count.

        Algorithm:
        - Identical cross product with COUNT of matching experiment rows.

        Complexity: O(E).
        """
        return self.sql_values

    sql_values = """
    SELECT p.platform, n.experiment_name,
           COUNT(e.experiment_id) AS num_experiments
    FROM (
        SELECT 'Android' AS platform UNION ALL
        SELECT 'IOS' UNION ALL SELECT 'Web'
    ) p
    CROSS JOIN (
        SELECT 'Reading' AS experiment_name UNION ALL
        SELECT 'Sports' UNION ALL SELECT 'Programming'
    ) n
    LEFT JOIN Experiments e
      ON e.platform = p.platform AND e.experiment_name = n.experiment_name
    GROUP BY p.platform, n.experiment_name;
    """
# @lc code=end

