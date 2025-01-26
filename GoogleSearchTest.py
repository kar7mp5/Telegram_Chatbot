from GoogleSearch import search

if __name__=="__main__":
    j = search("Google", num_results=100, lang="en", advanced=True)
    for i in j:
        print(i)