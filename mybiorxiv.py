import os
import json
from math import ceil

start_date = "2024-01-01"
end_date = "2024-01-13"

# Get the first one to obtain metadata, number of papers in total
os.system(f"wget -O biorxiv_data.json https://api.biorxiv.org/details/biorxiv/{start_date}/{end_date}/0")
f = json.load(open("biorxiv_data.json"))
total_number = f["messages"][0]["total"]
iters = ceil(total_number / 100)

categories = ["biochemistry", "bioinformatics", "biophysics"]
keywords = ["neural network", "generative model", "diffusion model", "flow matching", "protein dynamcs", "markov"]
paper_list = []
for i in range(iters):
    os.system(f"wget -O biorxiv_data.json https://api.biorxiv.org/details/biorxiv/{start_date}/{end_date}/{i * 100}")
    f = json.load(open("biorxiv_data.json"))
    for paper in f["collection"]:
        if paper["category"] in categories:
            for kw in keywords:
                if kw in paper["abstract"]:
                    paper_list.append(paper)
                    print(paper)

with open("biorxiv.txt", "w") as f:
    with open("template.html") as g:
        template = g.read()

        for i, paper_id in enumerate(paper_list):
            temp = template[:]
            result = paper_id
            title = result["title"]
            url = result["doi"]
            abstract = result["abstract"].replace("\n", " ") #result.summary.replace("\n", " ")
            authors = result["authors"] #get_authors(result.authors)
            categories = result["category"] #", ".join([str(c) for c in result.categories])

            temp = temp.replace("my-title", title)
            temp = temp.replace("my-abstract", abstract)
            temp = temp.replace("my-authors", authors)
            temp = temp.replace("my-categories", categories)
            temp = temp.replace("my-url", url)
            f.write(temp + "\n\n")
