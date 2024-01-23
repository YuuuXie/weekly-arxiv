import arxiv
import requests
import datetime
import yaml
from googletrans import Translator

def get_authors(authors, first_author=False):
    output = str()
    if first_author == False:
        output = ", ".join(str(author) for author in authors)
    else:
        output = authors[0]
    return output

def get_daily_papers(topic: str, query: str = "slam", max_results=2, cat=None, date_range=None):
    search_engine = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    #base_url = "https://arxiv.paperswithcode.com/api/v0/papers/"
    
    result_dict = {}
    search_results = search_engine.results()

    while True:
        try:
            print("search_results", search_results)
            for result in search_results:
                print("result", result)
        
                paper_id = result.get_short_id()
                paper_title = result.title
                paper_url = result.entry_id
        
                #code_url = base_url + paper_id
                paper_abstract = result.summary.replace("\n", " ")
                paper_authors = get_authors(result.authors)
                paper_first_author = get_authors(result.authors, first_author=True)
                primary_category = result.primary_category
                categories = result.categories
        
                if query not in paper_abstract.lower():
                    continue
        
                if cat is not None:
                    any_match = any([c in cat for c in categories])
                    if not any_match:
                        continue
        
                publish_time = result.published.date()
                if publish_time not in date_range:
                    break
                
                print(publish_time, paper_title, ".", paper_first_author, ".", primary_category)
        
        #        translator = Translator()
        #        translations = translator.translate(paper_title, dest='zh-cn')
        #        print(translations.text)
        
                # eg: 2108.09112v1 -> 2108.09112
                ver_pos = paper_id.find('v')
                if ver_pos == -1:
                    paper_key = paper_id
                else:
                    paper_key = paper_id[0:ver_pos]
        
                result_dict[paper_key] = result
            break
        except Exception as exception:
            print("Get error:", exception.__class__.__name__, exception)
            continue

    return result_dict 

today = datetime.date.today()
start_delta = datetime.timedelta(days=2, weeks=0)
today = today - start_delta

weekday = today.weekday()
date_range = []
for d in range(weekday):
    start_delta = datetime.timedelta(days=d+1, weeks=0)
    pastday = today - start_delta
    date_range.append(pastday)

print(date_range)

with open("topic.yml", "r") as stream:
    dct = yaml.safe_load(stream)

for topic in dct.keys():
    print("******************", topic, "*********************")
    print(dct[topic]["Title"])
    collected_paper_keys = []
    with open(topic + ".txt", "w") as f:
        for subtitle in dct[topic].keys():
            if subtitle == "Title": continue
            all_data = {}
            for query in dct[topic][subtitle].keys():
                data = get_daily_papers(
                    topic=topic, 
                    query=query,
                    max_results=float("inf"), 
                    cat=dct[topic][subtitle][query],
                    date_range=date_range,
                )
                paper_keys = list(data.keys())
                for k in paper_keys:
                    if k in collected_paper_keys:
                        data.pop(k)                    
                
                all_data.update(data)
                collected_paper_keys += list(data.keys())
        
            with open("template.html") as g:
                template = g.read()
        
            if len(all_data) > 0:
                subtitle_temp = f"""<p style="font-size: 18px;color: rgb(0,100,0);text-align:center">
          <strong style="visibility: visible;">{subtitle.capitalize()}</strong>
    </p>
    """
                f.write(subtitle_temp)
                print(subtitle)
    
                for i, paper_id in enumerate(all_data):
                    temp = template[:]
                    result = all_data[paper_id]
                    title = result.title
                    url = result.entry_id
                    abstract = result.summary.replace("\n", " ")
                    authors = get_authors(result.authors)
                    categories = ", ".join([str(c) for c in result.categories])
        
                    temp = temp.replace("my-title", title)
                    temp = temp.replace("my-abstract", abstract)
                    temp = temp.replace("my-authors", authors)
                    temp = temp.replace("my-categories", categories)
                    temp = temp.replace("my-url", url)
                    f.write(temp + "\n\n")
