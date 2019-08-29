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