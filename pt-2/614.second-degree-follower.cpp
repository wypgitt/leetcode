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
SELECT f1.followee AS follower, COUNT(DISTINCT f2.followee) AS num
FROM Follow f1
JOIN Follow f2 ON f2.follower = f1.followee
GROUP BY f1.followee
ORDER BY f1.followee;
)SQL";

/*
Interview explanation:
A second-degree follower is a user who is followed and also follows other users. Self-join where f1.followee = f2.follower, then count distinct people they follow.

C++ data structures: none; SQL is embedded as documentation and answer.

Edge cases: inner join excludes users with no outgoing follows. DISTINCT avoids duplicate relationship counts.

Complexity: database self-join cost; indexes on follower and followee are useful.
*/
