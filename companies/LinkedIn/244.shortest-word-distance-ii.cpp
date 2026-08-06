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


class WordDistance {
    unordered_map<string, vector<int>> positions;

public:
    WordDistance(vector<string>& wordsDict) {
        /*
        Approach: preprocess every word into a sorted list of its indices. A
        query compares the two sorted index lists with two pointers; advancing
        the smaller index is the only move that can reduce the current distance.

        C++ notes: unordered_map<string, vector<int>> is the direct equivalent of
        Python defaultdict(list) for word-to-positions storage.
        Complexity: O(n) preprocessing time/space; O(a+b) per query for the two
        occurrence counts.
        */
        for (int i = 0; i < (int)wordsDict.size(); ++i) positions[wordsDict[i]].push_back(i);
    }

    int shortest(string word1, string word2) {
        const vector<int>& a = positions[word1];
        const vector<int>& b = positions[word2];
        int i = 0, j = 0, best = INT_MAX;
        while (i < (int)a.size() && j < (int)b.size()) {
            best = min(best, abs(a[i] - b[j]));
            if (a[i] < b[j]) ++i;
            else ++j;
        }
        return best;
    }
};
