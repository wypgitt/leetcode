#include <algorithm>
#include <array>
#include <cmath>
#include <climits>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <random>
#include <regex>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

const char* SOLUTION_SQL = R"SQL(
WITH first_login AS (
    SELECT player_id, MIN(event_date) AS first_date
    FROM Activity
    GROUP BY player_id
)
SELECT ROUND(AVG(a.event_date IS NOT NULL), 2) AS fraction
FROM first_login f
LEFT JOIN Activity a
    ON a.player_id = f.player_id
   AND a.event_date = DATE_ADD(f.first_date, INTERVAL 1 DAY);
)SQL";

/*
Interview explanation:
Find each player's first login, then left join to an activity exactly one day later. Averaging the boolean match gives the returning fraction.

C++ data structures: none; SQL is embedded in a raw string.

Edge cases: LEFT JOIN keeps players who did not return and contributes 0 for them.

Complexity: database cost is driven by grouping per player and joining on (player_id,event_date); an index there is ideal.
*/
