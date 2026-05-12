#
# @lc app=leetcode id=1264 lang=python3
#
# [1264] Page Recommendations
#

# @lc code=start
from __future__ import annotations

try:
    import pandas as pd
except ImportError:  # Keeps the file importable in non-pandas LeetCode folders.
    pd = None


def page_recommendations(friendship: pd.DataFrame, likes: pd.DataFrame) -> pd.DataFrame:
    friends_from_left = friendship.loc[friendship["user1_id"] == 1, ["user2_id"]].rename(
        columns={"user2_id": "user_id"}
    )
    friends_from_right = friendship.loc[friendship["user2_id"] == 1, ["user1_id"]].rename(
        columns={"user1_id": "user_id"}
    )
    friends = pd.concat([friends_from_left, friends_from_right], ignore_index=True).drop_duplicates()

    liked_by_user = likes.loc[likes["user_id"] == 1, "page_id"]
    recommendations = friends.merge(likes, on="user_id")
    recommendations = recommendations.loc[~recommendations["page_id"].isin(liked_by_user), ["page_id"]]

    return recommendations.drop_duplicates().rename(columns={"page_id": "recommended_page"})


SQL_QUERY = """
SELECT DISTINCT l.page_id AS recommended_page
FROM Likes AS l
JOIN (
    SELECT user2_id AS user_id
    FROM Friendship
    WHERE user1_id = 1
    UNION
    SELECT user1_id AS user_id
    FROM Friendship
    WHERE user2_id = 1
) AS friends
    ON friends.user_id = l.user_id
WHERE l.page_id NOT IN (
    SELECT page_id
    FROM Likes
    WHERE user_id = 1
);
"""
# @lc code=end

# Explanation
# -----------
# This is a database problem. User 1's friends can appear in either friendship
# column, so first normalize both directions into a one-column friend table.
# Join those friend ids to Likes, remove pages already liked by user 1, and
# return distinct page ids as recommended_page.
#
# In Pandas, concat builds the normalized friend list, merge performs the join,
# isin filters out already-liked pages, and drop_duplicates implements DISTINCT.
# The SQL_QUERY constant expresses the same logic in SQL for the original
# LeetCode database version.
#
# Edge cases: a friend relation can be stored as (1, friend) or (friend, 1);
# multiple friends can like the same page; pages liked by user 1 must not be
# recommended even if many friends like them.
#
# Time complexity: O(F + L) average for filtering and joining, depending on the
# DataFrame engine. Space complexity: O(F + L) for intermediate tables.
