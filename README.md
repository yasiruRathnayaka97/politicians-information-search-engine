# politicians-inforamation-search-engine
## Structure of data:

Data required for indexing are scrapped from the website http://www.manthri.lk/si/politicians. Profile of a minister store as a document.Document structure as follows.

* name 
* party 
* district 
* contact_information (phone,email)
* age
* gender 
* position(type,subject) 
* biography

Age field generated in index time and birthday field and all the other fields generated at crawl time.

## Techniques:

### Rule base intention classifier:

The main objective of the classifier is to detect fields and selections of the search phrase. (ex: වයස අවුරුදු 40 ත් 60 ත් අතර ඇමතිවරුන්ගේ නම්)

* Fields : what does the user already know with values? (ex: age (වයස) is the  field and 40 and 60 are the values for the field)
* Selects : What does the user want to find?(ex: name(නම) is the selection)
	
The image classifier identifies terms with the proximity. It helps the classifier to guess which are  the fields and which are the selections. In addition to that the classifier.

In addition to the fields and selections the classifier identify terms related to range of values (ex: අතර ) and count of matching queries (ex: ගණන)


### Document Indexing techniques:

Create a custom analyzer ( “sinhala_analyzer”)  using elasticsearch which has the following characteristics.
  * Include filters for sinhala synonyms and stop words
  * Use standard tokenizer 
  * Use of explicit mapping without using dynamic mapping.Otherwise dynamic mapping interprets some fields (such as birthday) as text, which is wrong.

### Query processing techniques:
	
Use of longest contiguous matching subsequence to measure the similarity between terms. It helps to identify and correct  error terms (such as spelling mistakes) inside the query.

### Query optimization techniques:
	
Used following query types and etc… to obtain better results.

* Boosting : Used to control the score contribution of fields according to the importance of each field. 
(ex: if term “ඇමැති” inside the query field “position.type” should boost)
* Multi Match with cross-fields: Used to match multiple fields.
* Boolean queries: Used to search using both text and integer type fields.
* Range filters: Used to handle queries include Integer or date ranges.


## Main flow of indexing and searching phases:

### Indexing phase :

* Crawl the website and create corpus
* Index documents using custom analyzer and mapper

### Searching phase :

* Accept search phrase
* Process query to clean punctuation,error words etc…
* Identify intention (fields and selects) using rule base intention classifier.
* Create queries 
    * 2 advance queries -  Try to find results with many constraints. Output better results. (Use above query optimization techniques). Sometimes high constraints lead to not         having enough elasticsearch document hits.
    * 1 simple query - Create to avoid high constraint issue
* Search using the above 3 queries
* Show the results of advance queries if they delivered enough hits to show otherwise show the results of simple query

## Diagram of IR system:

![ES (2)](https://user-images.githubusercontent.com/57071700/142974218-3d31c93e-5fb8-400d-bdff-c153013bd132.png)


## Tech stack:

* Elasticsearch
* Scrappy
* Flask
