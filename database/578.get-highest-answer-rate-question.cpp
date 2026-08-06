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
SELECT question_id AS survey_log
FROM SurveyLog
GROUP BY question_id
ORDER BY SUM(action = 'answer') / SUM(action = 'show') DESC, question_id
LIMIT 1;
)SQL";

/*
Interview explanation:
For each question, answer rate is answers divided by shows. MySQL boolean expressions aggregate as 1/0, so SUM(action='answer') counts answers.

C++ data structures: none; SQL is stored as a raw string.

Edge cases: ordering by question_id makes ties deterministic.

Complexity: one grouped scan of SurveyLog; index on question_id can help grouping.
*/
