curami-v2
=========
Attempt to curate BioSamples objects.

In first version we are only interested of simple lexical correction of attributes. 

Here we focus on the characteristics section of the sample data.  
As a first step, we will ignore the IRI of attributes.  

### Collection
Similar to previous version, we start by collecting data. When we collect data from wwwdev environment its quite slow. 
If we try to increase the number of threads, server simply gives up responding. 
Therefore having a way to continue from last stopped position is handy. 
Currently we need to provide last collected file as an argument to achieve this.

First, retrieve all data through JSON API and save them in local file system.  
We will save the whole sample without changing its data.  

1. Collect data in small files and combine them to bigger file for easy handling  
2. Generate summary statistics of data, to understand data  

### Preprocess
First we will try to preprocess data(attributes) as much as possible to combine them.
Sample attributes contains different representations.
* Camel case attributes (collection date, collection_date, Collection_Date, COLLECTION_DATE, Collection date)
* Snake case attributes
* Attribute words separated by space
* Different uses of non-word characters (Age,'Age, cell-treatment, bmi (kg/m2), lot, lot#, cd8ccr7 cd45, %cd8ccr7+ cd45+, %cd8ccr7+ cd45-, %cd8ccr7-cd45 -, %cd8ccr7-cd45+)
* Different uses of metrics in attributes (weight kg, weight_kg, height m, height_m, Survival (days), Overall Survival (months), overall survival (months), Time (min), Age (years))

We will convert attributes into two representations and compare them to filter best attributes
1. Simple case conversion
* Remove leading non word characters (only - and ')
* Dash followed by underscore
* Remove double quotes
* Replace backward slash with forward slash and remove spaces around forward slash
* Replace underscore with space
* Strip leading, trailing and extra spaces
* Remove spaces inside parenthesis/brackets

2. Camel case to space separated words
* Convert camel case to snake case
* Then use all other steps in previous process

Then compare two processes for further matches

PIPELINE (automatic attribute curation)
Transform using two methods
compare two transformed entities, 
    if they are the same good, 
    if they are not check existing attribute for both of them, 
        if there are existing attribute select that one, 
        if there are no existing attributes sent through dictionary test,
            if dictionary test passed use that,
            if it failed use original attribute (should we try correct the spelling)


### Analysis
After pre-processing step we have attributes that adhere to similar format. 
In analysis step, first, we need to find syntactically similar pairs, to identify spelling mistakes, pluralisation etc...
* Use edit distance function to find syntactically similar pairs
* Use dictionary to find spelling mistakes of syntactically similar pairs




### Future

Add different scoring mechanisms, combine score to filter out best suggestions
Analyse important attributes - principal component analysis
Cluster samples (First into large clusters, then inside finer grade clusters)
User interface

 




-------------------------------------------------------------------------------
* attributes with metric in parenthesis [age vs age (days)]
* abbreviated values 


--------------------------------------------------------------------------------
In characteristics (attributes) section we have key value pairs. Once we ignored the IRI,  
We have attribute and its related values. Our main goal is to minimise number of attributes and values.  

###### How can we minimise number of attributes
* Have a style guide: (eg. instead of using "-" to separate words use " ")
* Misspelled words: rename back to correct spelling, no abbreviations
* Find duplicated attributes: this might require a look into corresponding values
* Ontology mapping: use zooma to get ontology, this might be a long shot


##### What can we do
* Find coocurrence of attributes
* Find synonyms, improve with ontology
* Cluster similar samples
* learn from curated samples ? what type of curation 
* Having an attribute and values dictionary
* Identify submitter, feedback about the errors, require changes ??
* Can we identify metrics


### Clustering
We have 40,000 different attributes. With 40k attributes clustering become almost impossible.

Dimensionality reduction is one popular technique to remove noisy (i.e. irrelevant) and
redundant attributes (AKA features). Dimensionality reduction techniques can be categorized mainly into feature extraction and feature selection. In feature extraction approach,
features are projected into a new space with lower dimensionality. Examples of feature
extraction technique include Principle Component Analysis (PCA), Linear Discriminant
Analysis (LDA), Singular Value Decomposition (SVD), to name a few. On the other hand,
the feature selection approach aims to select a small subset of features that minimize redundancy and maximize relevance to the target (i.e. class label). Popular feature selection
techniques include: Information Gain, Relief, Chi Squares, Fisher Score, and Lasso, to name
a few





source venv/bin/activate
pip3 freeze > requirements.txt
pip3 install -r requirements.txt
python3 setup.py sdist