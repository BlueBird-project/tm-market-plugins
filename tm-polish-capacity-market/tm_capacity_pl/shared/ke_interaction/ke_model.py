from ke_client import ki_split_uri, SplitURIBase


@ki_split_uri(uri_template="http://ke.bluebird.com/interval/${ts_from}/${ts_to}")
class KETimeIntervalUri(SplitURIBase):
    ts_from: int
    ts_to: int
