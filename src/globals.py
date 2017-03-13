# coding=utf-8

import os
import json
import gensim
import labellda

# TODO try to make it work with POST
# Might be because of Google App Engine restrictions
# Alternative: cache for presentation
PUBMED_FETCH_LIMIT = 170
PUBMED_SEARCH_URL = "https://www.ncbi.nlm.nih.gov/pubmed/?term="
PUBMED_ABSTRACT_FIELD_NAME = "AbstractText"
PUBMED_ID_FIELD_NAME = "PMID"
PUBMED_TITLE_FIELD_NAME = "ArticleTitle"
PUBMED_LABELS_FIELD_NAME = "MeshHeadingList"
PUBMED_PUBLISH_YEAR_FIELD_NAME = "Year" 
PUBMED_PUBLISH_MONTH_FIELD_NAME = "Month" 

TRAINED_MODEL_PATH = os.path.dirname(__file__) + "/static/models/training.lda"
CORPUS_PATH = os.path.dirname(__file__) + "/static/corpus/pubmed.mallet"
CORPUS_LABELS_PATH = os.path.dirname(__file__) + "/static/labels/pubmed.labels"
LLDA_MODEL_NAME = "labellda_model"

# These are only initialised once so we don't load them every
# time the UI sends a request
LDA_MODEL = gensim.models.LdaModel.load(TRAINED_MODEL_PATH)
LLDA_MODEL = labellda.STMT(LLDA_MODEL_NAME, epochs=400, mem=14000)

CORPUS = gensim.corpora.MalletCorpus(CORPUS_PATH)

WORDS_PER_TOPIC = 100

PROCESSED_CACHED_CORPUS = {}

# Need to normalise
TOPIC_PROB_THRESHOLD = 0.05
