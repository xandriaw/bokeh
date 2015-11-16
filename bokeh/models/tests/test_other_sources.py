import json
import pytest
from bokeh.models.sources import (
    DataSource,
    ServerDataSource,
)

## *************************
## ServerDataSource Tests
## *************************

def test_server_datasource_is_instance_of_datasource():
    ds = ServerDataSource()
    assert isinstance(ds, DataSource)
