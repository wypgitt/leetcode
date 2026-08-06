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
SELECT
    player_id,
    event_date,
    SUM(games_played) OVER (
        PARTITION BY player_id
        ORDER BY event_date
    ) AS games_played_so_far
FROM Activity;
)SQL";

/*
Interview explanation:
This database problem is best solved in SQL, stored here as a C++ raw string to keep the requested one-to-one .cpp translation. A window running SUM partitioned by player and ordered by date keeps one output row per activity row.

C++ data structures: none; the C++ file is a container for the SQL answer and explanation.

Complexity: database cost is dominated by sorting or scanning by (player_id, event_date). An index on those columns is the practical improvement.
*/
