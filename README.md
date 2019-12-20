# Article-Similarity-Ranker
The purpose of this program is to aid in the collection of relevant articles to include in a meta-analysis. This program will take as input a title of an article on google scholar and will output a ranked list of similar articles.


[tf-idf weighting](https://www.geeksforgeeks.org/tf-idf-model-for-page-ranking/) is used to rank article similarity. All articles that cite the input article are taken into consideration. Of these articles, the one whose abstract has the highest tf-idf score compared to the abstract of the input article is ranked highest. And so on the ranked similarity list is created in order of descending tf-idf scores.


## Requirements
* [Scholarly](https://pypi.org/project/scholarly/)
  * ```pip install scholarly```
* [Numpy](https://pypi.org/project/numpy/)
  * ```pip install numpy```
* [Scikit-Learn](https://pypi.org/project/scikit-learn/)
  * ```pip install scikit-learn```


## Usage
```similarity_ranker.py [-h] [--load] [--save] [--output] title```

positional arguments:

  	title       Title of article to be searched for on google scholar
optional arguments:

  	-h, --help  show this help message and exit
    
  	--load      Loads a previously stored search query from search_query.pk
    
  	--save      Saves the query locally to search_query.pk
    
  	--output    If this flag is set, the data will be saved in result.csv

