# coding=utf-8

import os

class Globals:
    PUBMED_SEARCH_URL = "https://www.ncbi.nlm.nih.gov/pubmed/?term="
    PUBMED_ABSTRACT_FIELD_NAME = "AbstractText"
    PUBMED_ID_FIELD_NAME = "PMID"
    PUBMED_PUBLISH_YEAR_FIELD_NAME = "Year" # Keep in mind this is not necessarily publish year, might be revise year, completion year. however this shouldn't affect us
    
    TRAINED_MODEL_PATH = os.path.dirname(__file__) + "/static/models/training.lda"
    CORPUS_PATH = os.path.dirname(__file__) + "/static/corpus/pubmed.mallet"

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
