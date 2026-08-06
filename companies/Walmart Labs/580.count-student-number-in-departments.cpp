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
SELECT d.dept_name, COUNT(s.student_id) AS student_number
FROM Department d
LEFT JOIN Student s ON s.dept_id = d.dept_id
GROUP BY d.dept_id, d.dept_name
ORDER BY student_number DESC, d.dept_name;
)SQL";

/*
Interview explanation:
Start from Department and LEFT JOIN students so departments with zero students remain. COUNT(student_id) ignores null joined rows.

C++ data structures: none; SQL is embedded in C++.

Edge cases: zero-student departments output count 0 and sort by department name after count.

Complexity: database join and grouping; index Student(dept_id) is the key optimization.
*/
