from googlesearch import search, SearchResult

query = "Python programming tutorials"
results = search(query, num_results=10)

for result in results:
    if isinstance(result, SearchResult):
        print(f"Link: {result.link}")
        print(f"Title: {result.title}")
        print(f"Description: {result.description}")
    else:
        print(f"Link: {result}")