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

class Solution {
public:
    int minimumSemesters(int n, vector<vector<int>>& relations) {
        vector<vector<int>> graph(n + 1);
        vector<int> indegree(n + 1, 0);

        for (const auto& relation : relations) {
            graph[relation[0]].push_back(relation[1]);
            ++indegree[relation[1]];
        }

        queue<int> q;
        for (int course = 1; course <= n; ++course) {
            if (indegree[course] == 0) q.push(course);
        }

        int semesters = 0;
        int taken = 0;
        while (!q.empty()) {
            int levelSize = q.size();
            ++semesters;
            while (levelSize--) {
                int course = q.front();
                q.pop();
                ++taken;

                for (int next : graph[course]) {
                    if (--indegree[next] == 0) q.push(next);
                }
            }
        }

        return taken == n ? semesters : -1;
    }
};

/*
Interview Explanation

Core idea:
Courses with no remaining prerequisites can be taken in the same semester.
This is topological sorting by BFS levels.

C++ data structures:
- vector<vector<int>> adjacency list stores prerequisite edges.
- vector<int> indegree counts remaining prerequisites for each course.
- queue<int> stores courses available for the current or future semester.

Algorithm:
1. Build graph and indegrees.
2. Enqueue all courses with indegree 0.
3. Each BFS level is one semester; process all currently available courses.
4. Decrease indegrees of dependent courses and enqueue newly available courses.
5. If all courses are processed, return semesters; otherwise a cycle exists.

Correctness:
A course enters the queue exactly when all prerequisites have been taken. All
courses in the same queue level can be taken simultaneously, so counting levels
counts semesters. If a cycle exists, its courses never reach indegree 0, so
taken < n and the answer is -1.

Complexity:
O(n + e) time and O(n + e) space.

Edge cases:
- No relations: all courses are taken in one semester.
- Cycle: returns -1.
- Multiple independent chains are processed in parallel by levels.
*/
