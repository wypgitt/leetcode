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
    vector<int> diffWaysToCompute(string expression) {
        /*
        Approach: divide and conquer on each operator. Recursively compute all
        results for the left and right expressions, then combine every pair with
        the operator. Memoization avoids recomputing the same substring.

        C++ notes: unordered_map<string, vector<int>> mirrors Python lru_cache.
        Complexity: Catalan-number output size; memoization stores each substring
        result list.
        */
        unordered_map<string, vector<int>> memo;
        function<vector<int>(const string&)> solve = [&](const string& expr) -> vector<int> {
            if (memo.count(expr)) return memo[expr];
            vector<int> results;
            for (int i = 0; i < (int)expr.size(); ++i) {
                char ch = expr[i];
                if (ch != '+' && ch != '-' && ch != '*') continue;
                vector<int> left = solve(expr.substr(0, i));
                vector<int> right = solve(expr.substr(i + 1));
                for (int a : left) for (int b : right) {
                    if (ch == '+') results.push_back(a + b);
                    else if (ch == '-') results.push_back(a - b);
                    else results.push_back(a * b);
                }
            }
            if (results.empty()) results.push_back(stoi(expr));
            memo[expr] = results;
            return results;
        };
        return solve(expression);
    }
};
