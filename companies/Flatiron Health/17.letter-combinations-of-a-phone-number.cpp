#include <algorithm>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>
using namespace std;


class Solution {
public:
    vector<string> letterCombinations(string digits) {
        /*
        Approach:
        Backtrack over the input digits. At each position choose one possible
        letter from that phone key, append it to the current path, and recurse to
        the next digit.

        C++ notes:
        The mapping is a vector<string> indexed by digit - '0'. The path string
        is mutated with push_back/pop_back to avoid repeated full copies.

        Complexity: O(4^n * n) time including output strings and O(n) stack.
        */
        if (digits.empty()) return {};
        vector<string> phone = {"", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"};
        vector<string> ans;
        string path;
        function<void(int)> dfs = [&](int index) {
            if (index == (int)digits.size()) {
                ans.push_back(path);
                return;
            }
            for (char ch : phone[digits[index] - '0']) {
                path.push_back(ch);
                dfs(index + 1);
                path.pop_back();
            }
        };
        dfs(0);
        return ans;
    }
};
