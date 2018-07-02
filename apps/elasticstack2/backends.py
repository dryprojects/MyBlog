# Copyright (c) 2014-2015, Ben Lopatin
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.  Redistributions in binary
# form must reproduce the above copyright notice, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided with
# the distribution

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from haystack.backends.elasticsearch2_backend import \
        Elasticsearch2SearchBackend, Elasticsearch2SearchEngine


class ConfigurableElasticBackend(Elasticsearch2SearchBackend):
    """
    Extends the Haystack ElasticSearch backend to allow configuration of index
    mappings and field-by-field analyzers.
    """
    DEFAULT_ANALYZER = "snowball"
    DEFAULT_NGRAM_SEARCH_ANALYZER = None
    DEFAULT_NGRAM_INDEX_ANALYZER = None

    def __init__(self, connection_alias, **connection_options):  # noqa
        super(ConfigurableElasticBackend, self).__init__(connection_alias, **connection_options)

        # user index settings

        global_settings_dict = getattr(settings, 'ELASTICSEARCH_INDEX_SETTINGS', None)
        if global_settings_dict:
            if 'settings' in global_settings_dict and 'SETTINGS_NAME' in connection_options:
                raise ImproperlyConfigured("You cannot specify ELASTICSEARCH_INDEX_SETTINGS['settings'] in settings "
                                           "and also 'SETTINGS_NAME' in your index connection '%s'. "
                                           "Use only one configuration way." % connection_alias)

            user_settings = None
            if 'settings' in global_settings_dict:
                user_settings = getattr(settings, 'ELASTICSEARCH_INDEX_SETTINGS', None)
            if 'SETTINGS_NAME' in connection_options:
                settings_name = connection_options.get('SETTINGS_NAME', None)
                if settings_name not in global_settings_dict:
                    raise ImproperlyConfigured("'SETTINGS_NAME' '%s' is missing in ELASTICSEARCH_INDEX_SETTINGS dict." % settings_name)
                user_settings = global_settings_dict.get(settings_name)

            if user_settings:
                setattr(self, 'DEFAULT_SETTINGS', user_settings)

        # user settings of analyzers

        if hasattr(settings, 'ELASTICSEARCH_DEFAULT_ANALYZER') and 'DEFAULT_ANALYZER' in connection_options:
            raise ImproperlyConfigured("You cannot specify ELASTICSEARCH_DEFAULT_ANALYZER in settings "
                                       "and also 'DEFAULT_ANALYZER' in your index connection '%s'. "
                                       "Use only one configuration way." % connection_alias)

        if hasattr(settings, 'ELASTICSEARCH_DEFAULT_NGRAM_SEARCH_ANALYZER') and 'DEFAULT_NGRAM_SEARCH_ANALYZER' in connection_options:
            raise ImproperlyConfigured("You cannot specify ELASTICSEARCH_DEFAULT_NGRAM_SEARCH_ANALYZER in settings "
                                       "and also 'DEFAULT_NGRAM_SEARCH_ANALYZER' in your index connection '%s'. "
                                       "Use only one configuration way." % connection_alias)

        user_analyzer = getattr(settings, 'ELASTICSEARCH_DEFAULT_ANALYZER', None) or \
            connection_options.get('DEFAULT_ANALYZER', None)
        ngram_search_analyzer = getattr(settings, 'ELASTICSEARCH_DEFAULT_NGRAM_SEARCH_ANALYZER', None) or \
            connection_options.get('DEFAULT_NGRAM_SEARCH_ANALYZER', None)
        ngram_index_analyzer = getattr(settings, 'ELASTICSEARCH_DEFAULT_NGRAM_INDEX_ANALYZER', None) or \
            connection_options.get('DEFAULT_NGRAM_INDEX_ANALYZER', None)
        if user_analyzer:
            setattr(self, 'DEFAULT_ANALYZER', user_analyzer)
        if ngram_search_analyzer:
            setattr(self, 'DEFAULT_NGRAM_SEARCH_ANALYZER', ngram_search_analyzer)
        if ngram_index_analyzer:
            setattr(self, 'DEFAULT_NGRAM_INDEX_ANALYZER', ngram_index_analyzer)

    def build_schema(self, fields):
        content_field_name, mapping = super(ConfigurableElasticBackend, self).build_schema(fields)

        for field_name, field_class in fields.items():
            field_mapping = mapping[field_class.index_fieldname]

            if field_mapping['type'] == 'string' and field_class.indexed:
                if not hasattr(field_class, 'facet_for') and not field_class.field_type in('ngram', 'edge_ngram'):
                    field_mapping['analyzer'] = getattr(field_class, 'analyzer', self.DEFAULT_ANALYZER)
                #这里给document为True的文档字段设置一下限制条件，因为elasticsearch2.x里string有最大长度限制，5.x版本里text没有长度限制
                #为了避免在分词后_all字段过长，这里不把document为True的字段的分词包含在_all中
                if not hasattr(field_class, 'facet_for') and not field_class.field_type in ('ngram', 'edge_ngram') and field_class.document == True:
                    field_mapping['include_in_all'] = False

                if not hasattr(field_class, 'facet_for') and field_class.field_type in('ngram', 'edge_ngram'):
                    if self.DEFAULT_NGRAM_SEARCH_ANALYZER:
                        field_mapping['search_analyzer'] = getattr(field_class, 'search_analyzer', self.DEFAULT_NGRAM_SEARCH_ANALYZER)
                    if self.DEFAULT_NGRAM_INDEX_ANALYZER:
                        field_mapping['analyzer'] = getattr(field_class, 'analyzer', self.DEFAULT_NGRAM_INDEX_ANALYZER)

            mapping.update({field_class.index_fieldname: field_mapping})
        return (content_field_name, mapping)


class ConfigurableElasticSearchEngine(Elasticsearch2SearchEngine):
    backend = ConfigurableElasticBackend
