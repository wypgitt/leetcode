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
    vector<vector<int>> richerThan;
    vector<int> answer;
    vector<int>* quietPtr;

    int dfs(int person) {
        if (answer[person] != -1) return answer[person];
        int best = person;
        for (int rich : richerThan[person]) {
            int cand = dfs(rich);
            if ((*quietPtr)[cand] < (*quietPtr)[best]) best = cand;
        }
        return answer[person] = best;
    }

public:
    vector<int> loudAndRich(vector<vector<int>>& richer, vector<int>& quiet) {
        int n = quiet.size();
        richerThan.assign(n, {});
        for (auto& e : richer) richerThan[e[1]].push_back(e[0]);
        answer.assign(n, -1);
        quietPtr = &quiet;
        for (int i = 0; i < n; ++i) dfs(i);
        return answer;
    }
};

/*
Interview explanation:
For each person, search all definitely richer ancestors in the DAG and memoize the quietest person reachable including themselves.

C++ data structures: vector<vector<int>> adjacency stores poorer -> richer edges; vector<int> answer is both result and memo table.

Edge cases: people with no richer known person return themselves. The graph is acyclic by problem statement.

Complexity: O(n+e) time and O(n+e) space.
*/
