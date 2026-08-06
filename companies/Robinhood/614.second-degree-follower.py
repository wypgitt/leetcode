#
# SQL solution stored in a Python file for this repository.
#

SOLUTION_SQL = """
SELECT f1.followee AS follower, COUNT(DISTINCT f2.followee) AS num
FROM Follow f1
JOIN Follow f2 ON f2.follower = f1.followee
GROUP BY f1.followee
ORDER BY f1.followee;
"""

"""
Interview explanation:
A second-degree follower is someone who follows at least one person and is also followed by someone. Join Follow to itself where f1.followee is f2.follower, then count distinct people that follower follows. The inner join naturally excludes users with no outgoing follows.

Edge cases: LEFT JOIN is used whenever zero-count rows must remain; COUNT(DISTINCT ...) is used where duplicate relationships could distort the logical count.
"""
