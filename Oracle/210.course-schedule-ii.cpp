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
    vector<int> findOrder(int numCourses, vector<vector<int>>& prerequisites) {
        /*
        Approach: Kahn topological sort. Start with indegree-zero courses, append
        each removed course to the order, and reduce indegrees of courses that
        depend on it. A cycle exists if fewer than numCourses are output.

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
        vector<int> order;
        while (!q.empty()) {
            int node = q.front(); q.pop();
            order.push_back(node);
            for (int nxt : graph[node]) if (--indegree[nxt] == 0) q.push(nxt);
        }
        return order.size() == (size_t)numCourses ? order : vector<int>{};
    }
};
