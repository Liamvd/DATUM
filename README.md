# Fair-Trauma-Reporting
This tool was made by FieldLab 8 as part of the course Data Science in Practice (2024), Leiden University, the Netherlands.

The Fair Trauma Reporting tool aims to facilitate researchers by automating the creation of metadata and labelling of new sources based on an input of ontologies and labes. The output is generated in csv, xml and rdf files which can be used for further data processing and analysing.

# How does it work
The tool takes in three kinds of input:
1. A list of ontologies
2. A list of labels
3. An event with some information

The user submits an event that they want to process, link, store and analyse. 
This input is pushed to an LLM model that links the event to one of the ontologies in the provided ontology list that best fits the event. 
Next, the LLM labels the event by going through all labels in the provided list and marks them as either true or false based on whether the event fits inside the label.
The LLM outputs the metadata generated about the event in a predefined structure. The tool further processes the metadata to make them exportable to the following formats:
1. xml
2. csv
3. rdf

The user is redirected to the result page from where they have the following options:
1. Copy the raw output (JSON format)
2. Create and download the output into the xml format
3. Create and download the output into the csv format
4. Create and download the output into the rdf format
5. Upload the rdf output to AllegroGraph
6. Process another event

When the user chooses to create and download into one of the three formats, two things happen: the output file is downloaded by the browser and a copy is created in the /output folder.
Be aware that it is necessary to first convert the output to the rdf format in order to send the metadata to AllegroGraph.

# How to use
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
3. Run app.py, open the web link and fill in the required information:
   1. Event name: Give a name to the event that you want to analyse, this could be anything and is just for naming purposes. Example: Violence on civilians
   2. Date: Give the date on which the event happened. Example: 1-8-2024
   3. Country: Give the country name where the event happened. Example: Sudan
   4. Region: Give the region name where the event happened. Example Khartoum
   5. Situation: Give a description of what happened during the event. This field is the one that is inputted in the LLM and should proivde as much detail as possible. Beside plain text, a url can also be submitted in this field

