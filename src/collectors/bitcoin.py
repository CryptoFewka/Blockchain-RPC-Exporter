import asyncio
from bitcoinrpc import BitcoinRPC
from helpers import strip_url
from time import perf_counter
from settings import cfg, logger


class bitcoin_collector():

    def __init__(self, https_url, provider):
        self.https_url = https_url
        self.labels = [
            'https_url', 'provider', 'blockchain', 'network_name',
            'network_type'
        ]
        self.labels_values = [
            https_url, provider, cfg.blockchain, cfg.network_name,
            cfg.network_type
        ]

    async def _probe(self, metrics):
        try:
            async with BitcoinRPC(self.https_url, "admin", "admin") as rpc:
                start = perf_counter()
                chain_info = await rpc.getblockchaininfo()
                latency = (perf_counter() - start) * 1000

                metrics['ws_rpc_health'].add_metric(self.labels_values, True)
                metrics['ws_rpc_latency'].add_metric(self.labels_values,
                                                     latency)
                metrics['ws_rpc_block_height'].add_metric(
                    self.labels_values, chain_info['headers'])
                metrics['ws_rpc_total_difficulty'].add_metric(
                    self.labels_values, chain_info['difficulty'])
        except Exception as exc:
            logger.error("Failed probing {} with error: {}".format(
                strip_url(self.url), exc))
            metrics['ws_rpc_health'].add_metric(self.labels_values, False)

    def probe(self, metrics):
        asyncio.run(self._probe(metrics))