package main

type Friendship struct {
	User1ID int
	User2ID int
}

type Like struct {
	UserID int
	PageID int
}

func pageRecommendations(friendships []Friendship, likes []Like) []int {
	friends := map[int]bool{}
	for _, f := range friendships {
		if f.User1ID == 1 {
			friends[f.User2ID] = true
		}
		if f.User2ID == 1 {
			friends[f.User1ID] = true
		}
	}

	likedByUser := map[int]bool{}
	for _, like := range likes {
		if like.UserID == 1 {
			likedByUser[like.PageID] = true
		}
	}

	recommended := map[int]bool{}
	for _, like := range likes {
		if friends[like.UserID] && !likedByUser[like.PageID] {
			recommended[like.PageID] = true
		}
	}

	ans := make([]int, 0, len(recommended))
	for page := range recommended {
		ans = append(ans, page)
	}
	return ans
}

const pageRecommendationsSQL = `
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
);`

/*
Explanation

LeetCode 1264 is originally a SQL/database problem. This Go file includes both
the original SQL query and an equivalent in-memory Go implementation.

The algorithm normalizes friendships in both directions to find all friends of
user 1. Then it builds a set of pages user 1 already likes. Finally, it scans
friends' likes and keeps distinct page ids that user 1 has not liked.

Go data structures: map[int]bool is used three times as a set: friend ids,
already-liked pages, and distinct recommendations.

Edge cases: friendships can store user 1 in either column; several friends can
like the same page; a page already liked by user 1 must be excluded.

Time complexity: O(F + L).
Space complexity: O(F + L) for the sets.
*/
