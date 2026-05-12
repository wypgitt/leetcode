package main

import (
	"net/url"
	"sync"
)

type HtmlParser interface {
	GetUrls(url string) []string
}

func crawl(startUrl string, htmlParser HtmlParser) []string {
	host := crawlerHost(startUrl)
	seen := map[string]bool{startUrl: true}
	var mu sync.Mutex
	var wg sync.WaitGroup

	var visit func(string)
	visit = func(page string) {
		defer wg.Done()
		for _, next := range htmlParser.GetUrls(page) {
			if crawlerHost(next) != host {
				continue
			}

			mu.Lock()
			if !seen[next] {
				seen[next] = true
				wg.Add(1)
				go visit(next)
			}
			mu.Unlock()
		}
	}

	wg.Add(1)
	go visit(startUrl)
	wg.Wait()

	ans := make([]string, 0, len(seen))
	for page := range seen {
		ans = append(ans, page)
	}
	return ans
}

func crawlerHost(raw string) string {
	parsed, _ := url.Parse(raw)
	return parsed.Host
}

/*
Explanation

This is a graph traversal where each HtmlParser.GetUrls call may block, so Go
goroutines are useful. A WaitGroup tracks active crawl tasks, and a mutex
protects the shared seen map.

The critical section is small: check whether a same-host URL is unseen, mark it
seen, and launch exactly one goroutine for it. Marking before launching avoids
duplicate work when multiple pages link to the same URL.

The WaitGroup starts with startUrl. Each discovered URL increments the counter
before its goroutine starts; each goroutine calls Done when finished.

Edge cases: repeated links, cycles, external host links, and arbitrary
completion order. Output order is intentionally unspecified.

Time complexity: O(V + E) over reachable same-host pages, ignoring network
latency.
Space complexity: O(V) for seen plus goroutine stack overhead.
*/
