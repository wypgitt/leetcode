#include <algorithm>
#include <array>
#include <climits>
#include <cmath>
#include <condition_variable>
#include <cstdlib>
#include <deque>
#include <functional>
#include <map>
#include <mutex>
#include <numeric>
#include <queue>
#include <set>
#include <sstream>
#include <stack>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

const string SQL_SOLUTION_1107 = R"SQL(
SELECT
    first_login AS login_date,
    COUNT(*) AS user_count
FROM (
    SELECT
        user_id,
        MIN(activity_date) AS first_login
    FROM Traffic
    WHERE activity = 'login'
    GROUP BY user_id
) AS first_logins
WHERE first_login BETWEEN DATE_SUB('2019-06-30', INTERVAL 90 DAY) AND '2019-06-30'
GROUP BY first_login;
)SQL";

/*
Interview Explanation

Core idea:
This is a SQL problem. Count users by the date of their first login, restricted
to first logins in the 90-day window ending on 2019-06-30.

Database data structures:
- The inner grouped query creates one row per user with MIN(activity_date).
- The outer GROUP BY aggregates those first-login rows by date.
- A useful index would be (activity, user_id, activity_date) or
  (user_id, activity, activity_date), depending on the engine.

Correctness:
The inner query filters to login events and computes each user's earliest login
date. The outer query keeps only first-login dates inside the required window
and counts how many users have each such date. Therefore each user is counted
once on exactly their first login day.

Complexity:
Conceptually the database scans login rows, groups by user_id, then groups the
result by date. Physical runtime depends on indexes and optimizer choices.

Edge cases:
- Users with no login activity are excluded.
- Multiple logins on the same first day count once.
- First logins before the 90-day window are excluded even if the user logged in
  during the window.
*/
