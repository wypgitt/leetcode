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
    int minimumLengthEncoding(vector<string>& words) {
        unordered_set<string> useful(words.begin(), words.end());
        for (const string& word : words) {
            for (int i = 1; i < (int)word.size(); ++i) useful.erase(word.substr(i));
        }
        int ans = 0;
        for (const string& word : useful) ans += word.size() + 1;
        return ans;
    }
};

/*
Interview explanation:
A word is unnecessary if it is a suffix of another word. Remove every proper suffix from the candidate set and encode only remaining words.

C++ data structures: unordered_set<string> deduplicates words and supports average O(1) erase.

Edge cases: duplicate words count once; proper suffix iteration starts at index 1 so a word does not erase itself.

Complexity: O(sum len(word)^2) with substring creation; O(total length) space.
*/
