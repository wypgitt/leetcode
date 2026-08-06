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

class Solution {
    vector<int> color;
    vector<vector<int>>* g;

    bool dfs(int node) {
        if (color[node] != 0) return color[node] == 2;
        color[node] = 1;
        for (int nei : (*g)[node]) if (!dfs(nei)) return false;
        color[node] = 2;
        return true;
    }

public:
    vector<int> eventualSafeNodes(vector<vector<int>>& graph) {
        g = &graph;
        color.assign(graph.size(), 0);
        vector<int> ans;
        for (int i = 0; i < (int)graph.size(); ++i) if (dfs(i)) ans.push_back(i);
        return ans;
    }
};

/*
Interview explanation:
A node is safe if all paths from it avoid cycles. DFS coloring detects gray-node revisits as cycles and memoizes nodes proven safe.

C++ data structures: vector<int> color uses 0=unvisited, 1=visiting, 2=safe.

Edge cases: terminal nodes have no outgoing edges and become safe immediately; self-loops are unsafe.

Complexity: O(V+E) time and O(V) space.
*/
