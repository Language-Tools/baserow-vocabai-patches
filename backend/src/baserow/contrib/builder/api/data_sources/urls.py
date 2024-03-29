from django.urls import re_path

from baserow.contrib.builder.api.data_sources.views import (
    DataSourcesView,
    DataSourceView,
    MoveDataSourceView,
)

app_name = "baserow.contrib.builder.api.data_sources"

urlpatterns = [
    re_path(
        r"page/(?P<page_id>[0-9]+)/data-sources/$",
        DataSourcesView.as_view(),
        name="list",
    ),
    re_path(
        r"data-source/(?P<data_source_id>[0-9]+)/$",
        DataSourceView.as_view(),
        name="item",
    ),
    re_path(
        r"data-source/(?P<data_source_id>[0-9]+)/move/$",
        MoveDataSourceView.as_view(),
        name="move",
    ),
]
