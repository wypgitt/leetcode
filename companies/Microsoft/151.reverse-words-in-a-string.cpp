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
    string reverseWords(string s) {
        /*
        Approach: parse whitespace-separated words, then append them in reverse
        order with single spaces. This matches Python split(), which removes
        leading/trailing spaces and collapses repeated spaces.

        C++ notes: stringstream tokenizes by whitespace.
        Complexity: O(n) time, O(n) space.
        */
        stringstream ss(s);
        vector<string> words;
        string word;
        while (ss >> word) words.push_back(word);
        string ans;
        for (int i = (int)words.size() - 1; i >= 0; --i) {
            if (!ans.empty()) ans.push_back(' ');
            ans += words[i];
        }
        return ans;
    }
};
