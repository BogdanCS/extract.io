# coding=utf-8

import os
import gensim

class Globals:
    # TODO try to make it work with POST
    # Might be because of Google App Engine restrictions
    # Alternative: cache for presentation
    PUBMED_FETCH_LIMIT = 170
    PUBMED_SEARCH_URL = "https://www.ncbi.nlm.nih.gov/pubmed/?term="
    PUBMED_ABSTRACT_FIELD_NAME = "AbstractText"
    PUBMED_ID_FIELD_NAME = "PMID"
    PUBMED_LABELS_FIELD_NAME = "MeshHeadingList"
    PUBMED_PUBLISH_YEAR_FIELD_NAME = "Year" # Keep in mind this is not necessarily publish year, might be revise year, completion year. however this shouldn't affect us
    
    TRAINED_MODEL_PATH = os.path.dirname(__file__) + "/static/models/training.lda"
    CORPUS_PATH = os.path.dirname(__file__) + "/static/corpus/pubmed.mallet"
    CORPUS_LABELS_PATH = os.path.dirname(__file__) + "/static/labels/pubmed.labels"

    # These are only initialised once so we don't load them every
    # time the UI sends a request
    LDA_MODEL = gensim.models.LdaModel.load(TRAINED_MODEL_PATH)
    CORPUS = gensim.corpora.MalletCorpus(CORPUS_PATH)
    
    PROCESSED_CACHED_CORPUS = {}

    LLDA_MODEL_NAME = "labellda_model"
    LLDA_MODEL = labellda.STMT(LLDA_MODEL_NAME, epochs=400, mem=14000)

# To delete
    _1_DAY = 86400  # 24 * 60 * 60 seconds
    _1_WEEK = 604800  # 7 * 24 * 60 * 60 seconds
    _1_MONTH = 2592000  # 30 * 24 * 60 * 60 seconds
    _10_MINUTES = 600  # seconds

    DEFAULT_LIMIT = 5

    MAX_REQUESTS = 5

    DUAL_LAYER_MEMCACHE_AND_IN_APP_MEMORY_CACHE = 0 # Cache in both memcache and cachepy by default
    SINGLE_LAYER_MEMCACHE_ONLY = 1
    SINGLE_LAYER_IN_APP_MEMORY_CACHE_ONLY = 2
