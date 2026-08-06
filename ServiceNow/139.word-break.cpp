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
    bool wordBreak(string s, vector<string>& wordDict) {
        /*
        Approach: dp[i] means s[0:i] can be segmented. For each position, test
        only word lengths that exist in the dictionary; if s[i-len:i] is a word
        and dp[i-len] is true, dp[i] becomes true.

        C++ notes: unordered_set<string> gives average O(1) word lookup; another
        unordered_set<int> stores distinct word lengths.
        Complexity: O(n * L * substring cost) time, O(n + dictionary) space.
        */
        unordered_set<string> words(wordDict.begin(), wordDict.end());
        unordered_set<int> lengths;
        for (const string& word : words) lengths.insert(word.size());
        vector<bool> dp(s.size() + 1, false);
        dp[0] = true;
        for (int i = 1; i <= (int)s.size(); ++i) {
            for (int len : lengths) {
                if (i >= len && dp[i - len] && words.count(s.substr(i - len, len))) {
                    dp[i] = true;
                    break;
                }
            }
        }
        return dp.back();
    }
};
