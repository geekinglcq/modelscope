# Copyright (c) Alibaba, Inc. and its affiliates.

from pathlib import Path

MODELSCOPE_URL_SCHEME = 'http://'
DEFAULT_MODELSCOPE_DOMAIN = 'www.modelscope.cn'
DEFAULT_MODELSCOPE_DATA_ENDPOINT = MODELSCOPE_URL_SCHEME + DEFAULT_MODELSCOPE_DOMAIN

DEFAULT_MODELSCOPE_GROUP = 'damo'
MODEL_ID_SEPARATOR = '/'
FILE_HASH = 'Sha256'
LOGGER_NAME = 'ModelScopeHub'
DEFAULT_CREDENTIALS_PATH = Path.home().joinpath('.modelscope', 'credentials')
API_RESPONSE_FIELD_DATA = 'Data'
API_RESPONSE_FIELD_GIT_ACCESS_TOKEN = 'AccessToken'
API_RESPONSE_FIELD_USERNAME = 'Username'
API_RESPONSE_FIELD_EMAIL = 'Email'
API_RESPONSE_FIELD_MESSAGE = 'Message'


class Licenses(object):
    APACHE_V2 = 'Apache License 2.0'
    GPL_V2 = 'GPL-2.0'
    GPL_V3 = 'GPL-3.0'
    LGPL_V2_1 = 'LGPL-2.1'
    LGPL_V3 = 'LGPL-3.0'
    AFL_V3 = 'AFL-3.0'
    ECL_V2 = 'ECL-2.0'
    MIT = 'MIT'


class ModelVisibility(object):
    PRIVATE = 1
    INTERNAL = 3
    PUBLIC = 5
