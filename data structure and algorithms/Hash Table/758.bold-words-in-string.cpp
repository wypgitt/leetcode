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
    string boldWords(vector<string>& words, string s) {
        vector<bool> bold(s.size(), false);
        for (const string& word : words) {
            size_t pos = s.find(word);
            while (pos != string::npos) {
                for (int i = pos; i < (int)pos + (int)word.size(); ++i) bold[i] = true;
                pos = s.find(word, pos + 1);
            }
        }
        string ans;
        for (int i = 0; i < (int)s.size();) {
            if (!bold[i]) ans += s[i++];
            else {
                ans += "<b>";
                while (i < (int)s.size() && bold[i]) ans += s[i++];
                ans += "</b>";
            }
        }
        return ans;
    }
};

/*
Interview explanation:
Mark every character covered by any word occurrence, then wrap each maximal marked interval in one bold tag pair. This merges overlapping and adjacent matches automatically.

C++ data structures: vector<bool> is compact coverage storage; string::find locates occurrences.

Edge cases: no marked characters returns the original string; overlapping words form one interval.

Complexity: direct matching can be O(words * occurrences * word length); output pass is O(n). Space is O(n).
*/
