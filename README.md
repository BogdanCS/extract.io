# extract.io
University of Manchester 3rd Year Project

# Backlog
(https://easybacklog.com/accounts/19201/backlogs/223216#Backlog)

# Information to extract

1. Compare topic distribution between decades (temporal trends)
2. Compare topic distribution between institutions (geographic trends)
3. Find relationships(correlation, causation) between different topics
	e.g 2 topics mentioned often together
4. Most common topics(?)
5. Correlation between other readily avialable statistics (e.g percentage of people
engaging in physical activity, percentage of smokers) and diseases like obesity
6. Citation analysis
7. Fraction of articles per year on topic (temporal trends)
8. Predicting MeSH headings for new abstracts
9. Predicting trends (i.e which words will be added to the MeSH ontology)

# Handling abbreviations

77% of MEDLINE abstracts have long form (short form)
1% have short form (long form)
22% don't have the long form defined in the text  

We could use AcroMine to help identify the abbreviations.
We need to find a way to normalise all the forms that refer to a single concept

# Implementation

1. LDA
2. TermMine
3. Linked LDA
4. D3.js for visualisation
 
nactem.ac.uk

# Evaluation

1. TREC?

# Visualisation

# Sources

[Topic models for MeSH research paper](http://www.ics.uci.edu/~newman/pubs/Newman-AI09.pdf)
[Trends in Pubmed](./p954-moerchen.pdf)
[Trends in Pubmed 2](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2656084/)
[Extensions](https://bugra.github.io/work/notes/2015-02-21/topic-modeling-for-the-uninitiated/)
[TM vs Term recognition 1](http://istina.msu.ru/media/publications/articles/c31/b23/3542979/ecir.pdf)
[TM on unstructured text, then NE recognition](http://s3.amazonaws.com/mairesse/research/papers/is11-lda.pdf)
[D3.js example](https://github.com/mlvl/Hierarchie)
[D3.js main](http://tt-history.appspot.com/)
[D3.js map](http://bl.ocks.org/lokesh005/7640d9b562bf59b561d6)

#TODO

1. Pass document name to the UI as well, along with the document URL
