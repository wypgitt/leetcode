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
    vector<vector<string>> partition(string s) {
        /*
        Approach: precompute pal[i][j], whether s[i..j] is a palindrome, then
        backtrack all cuts. A substring is added only if the precomputed table
        says it is valid, avoiding repeated palindrome scans.

        C++ notes: vector<vector<bool>> stores the DP table, and substr creates
        the chosen partition piece.
        Complexity: O(n^2 + output size * n) time, O(n^2) space plus recursion.
        */
        int n = s.size();
        vector<vector<bool>> pal(n, vector<bool>(n, false));
        for (int i = n - 1; i >= 0; --i) {
            for (int j = i; j < n; ++j) {
                pal[i][j] = s[i] == s[j] && (j - i < 2 || pal[i + 1][j - 1]);
            }
        }
        vector<vector<string>> ans;
        vector<string> path;
        function<void(int)> dfs = [&](int start) {
            if (start == n) { ans.push_back(path); return; }
            for (int end = start; end < n; ++end) {
                if (!pal[start][end]) continue;
                path.push_back(s.substr(start, end - start + 1));
                dfs(end + 1);
                path.pop_back();
            }
        };
        dfs(0);
        return ans;
    }
};
