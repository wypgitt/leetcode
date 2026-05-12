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

const string SQL_SOLUTION_1112 = R"SQL(
SELECT
    student_id,
    course_id,
    grade
FROM (
    SELECT
        student_id,
        course_id,
        grade,
        ROW_NUMBER() OVER (
            PARTITION BY student_id
            ORDER BY grade DESC, course_id ASC
        ) AS row_num
    FROM Enrollments
) AS ranked
WHERE row_num = 1
ORDER BY student_id;
)SQL";

/*
Interview Explanation

Core idea:
This is a SQL ranking problem. For each student, choose the row with highest
grade; ties are broken by smallest course_id.

Database data structures:
- ROW_NUMBER with PARTITION BY student_id ranks rows independently per student.
- ORDER BY grade DESC, course_id ASC encodes both the primary and tie-break
  requirements.

Correctness:
Within each student partition, row_num = 1 is exactly the highest grade row,
and if several rows share that grade, the smallest course_id comes first.
Filtering to row_num = 1 returns one correct row per student.

Complexity:
The database sorts or indexes rows within each student partition. A practical
index is (student_id, grade DESC, course_id ASC), though exact runtime depends
on the SQL engine.

Edge cases:
- A student with one course is returned.
- Grade ties choose the smaller course id.
- Final ORDER BY student_id matches required output order.
*/
