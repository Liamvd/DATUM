# Fair-Trauma-Reporting
This tool was made by FieldLab 8 as part of the course Data Science in Practice (2024), Leiden University, the Netherlands.

The Fair Trauma Reporting tool aims to facilitate researchers by automating the creation of metadata of new sources based on an input of ontologies and labes. The output is generated in csv, xml and rdf files which can be used for further data processing and analysing.


# How to use:
1. Ensure that a file with ontologies is present in the sources folder. The file needs to adhere to the following requirements: 
   1. be an Excel file called 'Ontologies.xlsx',
   2. there needs to be a tab called 'All', which has all the ontologies listed,
   3. the tab needs to have two columns named: 
      1. 'Ontology Concept': names of all ontologies),
      2. 'Description': list of labels 
      
   These requirements can be changed by editing the 'readOntologies()' (change ontology file type), 'promptRequest()' (change ontology file tab and column names) and 'runllm()' (change ontology file name) functions in llm.py.
2. Have a .env file present in the root of the project (same level as python files) that has the following variables defined: 
   1. API_KEY: key of the API that you are using, the tool currently uses the gemini-1.5-flash model. If you want to use another model made by Google, change the model value in function 'configureAi() in llm.py'. Using a model from a different company requires changes to both the 'configureAi()' and 'promptRequest()' functions in llm.py
   2. ag_admin: username of AllegroGraph cloud server
   3. ag_password: password of AllegroGraph cloud server
   4. ag_url: url of AllegroGraph cloud server (Example: abcd1234.allegrograph.cloud)
   5. ag_repo: name of the repository in AllegroGraph to which the rdf needs to be sent
   
   The last 4 requirements are not needed if the user does not want to utilise the AllegroGraph connection
3. Create a folder named 'output' in the root of the project (same level as python files), otherwise, no metadata can be exported