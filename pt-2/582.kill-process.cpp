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
public:
    vector<int> killProcess(vector<int>& pid, vector<int>& ppid, int kill) {
        unordered_map<int, vector<int>> children;
        for (int i = 0; i < (int)pid.size(); ++i) children[ppid[i]].push_back(pid[i]);
        vector<int> ans;
        queue<int> q;
        q.push(kill);
        while (!q.empty()) {
            int cur = q.front(); q.pop();
            ans.push_back(cur);
            for (int child : children[cur]) q.push(child);
        }
        return ans;
    }
};

/*
Interview explanation:
Killing a process kills its whole subtree in the parent-child forest. Build parent -> children adjacency, then BFS from the killed process.

C++ data structures: unordered_map<int, vector<int>> stores sparse child lists; queue<int> performs level traversal.

Edge cases: a leaf process returns only itself.

Complexity: O(n) build time plus O(k) traversal for killed descendants; O(n) space.
*/
