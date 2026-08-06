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
SELECT c.name
FROM Candidate c
JOIN Vote v ON v.candidateId = c.id
GROUP BY c.id, c.name
ORDER BY COUNT(*) DESC
LIMIT 1;
)SQL";

/*
Interview explanation:
Join votes to candidates, group by candidate, and take the largest count. The original problem guarantees a winner.

C++ data structures: none; SQL is embedded for repository consistency.

Edge cases: if ties were possible, RANK would be needed instead of LIMIT 1.

Complexity: database grouping cost depends on Vote size; an index on Vote(candidateId) helps.
*/
