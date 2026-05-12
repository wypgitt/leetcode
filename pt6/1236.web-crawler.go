package main

import (
	"net/url"
)

type HtmlParser interface {
	GetUrls(url string) []string
}

func crawl(startUrl string, htmlParser HtmlParser) []string {
	host := hostname(startUrl)
	seen := map[string]bool{startUrl: true}
	queue := []string{startUrl}

	for head := 0; head < len(queue); head++ {
		current := queue[head]
		for _, next := range htmlParser.GetUrls(current) {
			if !seen[next] && hostname(next) == host {
				seen[next] = true
				queue = append(queue, next)
			}
		}
	}

	ans := make([]string, 0, len(seen))
	for page := range seen {
		ans = append(ans, page)
	}
	return ans
}

func hostname(raw string) string {
	parsed, _ := url.Parse(raw)
	return parsed.Host
}

/*
Explanation

This is graph traversal. Start from startUrl, call HtmlParser.GetUrls for each
visited page, and enqueue only unseen URLs with the same hostname.

The queue gives BFS traversal, while the seen map prevents cycles and duplicate
parser calls. Host filtering uses net/url so paths on the same host are kept
and different domains are ignored.

The output order is arbitrary by problem statement, so collecting from a map is
fine. A trailing slash remains part of the URL string, so the seen map treats
"a" and "a/" as different pages, matching the problem.

Edge cases: no outgoing links; repeated links; external links; cycles.

Time complexity: O(V + E) over reachable same-host pages.
Space complexity: O(V).
*/
