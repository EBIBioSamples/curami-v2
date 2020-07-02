Attributes
collection date, collection_date, Collection date, COLLECTION_DATE, Collection_Date, *colection date*
catalog #
83c.25r.



- we tried to remove all non word characters, but results didnt look good. (re.sub(r"[^\w]", " ", attribute))
There are lot of strange attribute names depend on different non-wor characters. 
Eg. catalog #, 83c.25r. 
- Converting from camel case to snake case is not 100 percent successful. Some attributes lost their structure. Eg. . 
But this process generated lot of useful attributes, and we cant lose information stored in camel cased values by simply turning it to lower case.
Therefore lower case cleaning compared against camel case cleaning. Selected best from both. Too much ugly code though. 


first value is already in the set: key = BioSample_number, first[y] = biosample number , second = bio sample number
first value is already in the set: key = BioSample_ID, first[y] = biosample id , second = bio sample id
When we compare cleanup process, consider following example because BioSample is not int abbreviation list 
(missing s in BioSamples) we lost that capitalization. 


cant help with: TestResult3, ['testresult3', 'test result3']
cant decide with dictionary test




Organism,organism,133495
Organism and organism has appeared 133,495 times together


Clustering
==========

It is clear from the clustering results that considering only the existence of the attribute is not sufficient 
to get a satisfactory result. Therefore looking at the values of the attributes is important. Since each of the 
attribute contains large number of values, limiting number of values is inevitable. 
Another useful test would be to consider each of the sample as a document and use text classification tools. 
Transforming sample into a document will move the problem into a more familiar setup and make analysis easier.
Word embedding in particular can very effective. I'm leaving this document approach as the next level as before 
moving into another clustering approach, I need to get a result for the initial clustering and have a set of 
meaningful checklist of attributes for each cluster. At first we will not focus on the quality of the these 
checklist as this is only a guideline of how the entire pipeline should look like. 

How do we measure the quality of the clustering
-----------------------------------------------
- Silhouette method
- SSE: sum of the square error from the items of each cluster.
- Inter cluster distance: sum of the square distance between each cluster centroid.
- Intra cluster distance for each cluster: sum of the square distance from the items of each cluster to its centroid.
- Maximum Radius: largest distance from an instance to its cluster centroid.
- Average Radius: sum of the largest distance from an instance to its cluster centroid divided by the number of clusters. 
