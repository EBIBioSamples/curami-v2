###Collection
First, retrieve all data through JSON API and save them in local file system.
We will save the whole sample without changing its data.

###Preprocess
Convert to simple case (will lose some info)
replace underscores with space
trim: strip leading and trailing spaces
replace multiple spaces with single space

###Analysis
Here we focus on the characteristics section of the sample data.
As a first step, we will ignore the IRI of attributes.





1. Collect data in small files and combine them to bigger file for easy handling
2. Generate summary statistics of data, to understand data




-------------------------------------------------------------------------------
* attributes with metric in parenthesis [age vs age (days)]
* abbreviated values 





--------------------------------------------------------------------------------
In characteristics (attributes) section we have key value pairs. Once we ignored the IRI,
We have attribute and its related values. Our main goal is to minimise number of attributes and values.
###### How can we minimise number of
* Have a style guide: instead of using "-" to separate words use " "
* Misspelled words: rename back to correct spelling, no abbreviations
* Find duplicated attributes: this might require a look into corresponding values
* Ontology mapping: use zooma to get ontology, this might be a long shot


##### What can we do
* Find coocurrance of attributes
* Find synonyms, improve with ontology
* Cluster similar samples
* learn from curated samples ? what type of curation 
* Having an attribute and values dictionary
* Identfy submitter, feedback about the errors, require changes ??