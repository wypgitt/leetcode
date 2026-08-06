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
SELECT ROUND(SUM(tiv_2016), 2) AS tiv_2016
FROM Insurance
WHERE tiv_2015 IN (
    SELECT tiv_2015
    FROM Insurance
    GROUP BY tiv_2015
    HAVING COUNT(*) > 1
)
AND (lat, lon) IN (
    SELECT lat, lon
    FROM Insurance
    GROUP BY lat, lon
    HAVING COUNT(*) = 1
);
)SQL";

/*
Interview explanation:
Keep policies whose 2015 investment value is shared by another policy while their location pair is unique, then sum 2016 investment.

C++ data structures: none; this C++ file stores SQL as a raw string because the problem is database-only.

Edge cases: location uniqueness must use the (lat,lon) pair, not either column independently.

Complexity: database grouped subqueries; indexes on tiv_2015 and (lat,lon) improve performance.
*/
