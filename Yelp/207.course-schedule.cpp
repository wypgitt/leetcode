#include <algorithm>
#include <array>
#include <cctype>
#include <climits>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;


class Solution {
public:
    bool canFinish(int numCourses, vector<vector<int>>& prerequisites) {
        /*
        Approach: topological sort with indegrees. Courses with indegree zero can
        be taken now. Removing them decreases dependent courses' indegrees. If we
        take all courses, no cycle blocks completion.

        C++ notes: vector<vector<int>> is the adjacency list; queue<int> stores
        available courses.
        Complexity: O(V + E) time, O(V + E) space.
        */
        vector<vector<int>> graph(numCourses);
        vector<int> indegree(numCourses, 0);
        for (auto& edge : prerequisites) {
            graph[edge[1]].push_back(edge[0]);
            ++indegree[edge[0]];
        }
        queue<int> q;
        for (int i = 0; i < numCourses; ++i) if (indegree[i] == 0) q.push(i);
        int taken = 0;
        while (!q.empty()) {
            int node = q.front(); q.pop();
            ++taken;
            for (int nxt : graph[node]) if (--indegree[nxt] == 0) q.push(nxt);
        }
        return taken == numCourses;
    }
};
