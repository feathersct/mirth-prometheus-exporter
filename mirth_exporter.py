import json
import os
import time
from prometheus_client.core import CounterMetricFamily, GaugeMetricFamily, REGISTRY
from prometheus_client import start_http_server, GC_COLLECTOR, PLATFORM_COLLECTOR, PROCESS_COLLECTOR
import urllib3
from mirthpy.mirthService import MirthService
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# config file paths
dir_path = os.path.dirname(os.path.realpath(__file__))
config = json.load(open(os.path.join(dir_path, 'mirthConfig.json')))

class MirthStatsCollector(object):
    def __init__(self):
        pass
    def collect(self):
        # metrics to gather
        messageRec = GaugeMetricFamily("mirth_messages_received_total", "How many messages every poll have been received (per channel).", labels=["instance", "channelName", "channelId"])
        messageSent = GaugeMetricFamily("mirth_messages_sent_total", "How many messages every poll have been sent (per channel).", labels=["instance", "channelName", "channelId"])
        messageFiltered = GaugeMetricFamily("mirth_messages_filtered_total", "How many messages every poll have been filtered (per channel).", labels=["instance", "channelName", "channelId"])
        messageQueued = GaugeMetricFamily("mirth_messages_queued", "How many messages are currently queued (per channel).", labels=["instance", "channelName", "channelId"])
        messageError = GaugeMetricFamily("mirth_messages_errored_total", "How many messages every poll have errored (per channel).", labels=["instance", "channelName", "channelId"])
        memoryGauge = GaugeMetricFamily("mirth_server_size", "Mirth server storage size. Metric in bytes.", labels=["instance"])
        mirthServerStateGauge = GaugeMetricFamily("mirth_server_state", "Mirth server state, 0 means mirth server is up & 1 means mirth server down", labels=["instance"])

        # instance to poll, held in mirthConfig.json file
        instance = config['instance']

        # initialize mirth api
        service = MirthService(instance=instance, username=config['username'], password=config['password'])

        ableToOpen = False

        # attempt to open connection to mirth
        try:
            service.open()
            mirthServerStateGauge.add_metric([instance], 0) # 0 -> up
            systemStats = service.getSystemStats() # get storage bytes
            memoryGauge.add_metric([instance], systemStats.diskTotalBytes - systemStats.diskFreeBytes)
            ableToOpen = True
        except Exception as e:
            mirthServerStateGauge.add_metric([instance], 1) # 1 -> down
            service.close()

        # gather statistics on channels
        if ableToOpen:
            channelIdsAndNames = service.getChannelIdsAndNames()
            for stats in service.getChannelStatistics().channelStatistics:
                # try to find channel name and id
                channelIdName = [(c.id, c.name) for c in channelIdsAndNames.idsAndNames if c.id == stats.channelId]

                # continue if can't find it
                if len(channelIdName) == 0:
                    continue

                channelId, channelName = channelIdName[0]

                # add to prometheus
                messageRec.add_metric([instance, channelName, channelId], int(stats.received))
                messageSent.add_metric([instance, channelName, channelId], int(stats.sent))
                messageError.add_metric([instance, channelName, channelId], int(stats.error))
                messageFiltered.add_metric([instance, channelName, channelId], int(stats.filtered))
                messageQueued.add_metric([instance, channelName, channelId], int(stats.queued))

            service.close()

        # push metrics to end point
        yield messageRec
        yield messageSent
        yield messageError
        yield messageFiltered
        yield messageQueued
        yield mirthServerStateGauge
        yield memoryGauge

if __name__ == "__main__":
    start_http_server(config['prometheusPort'])
    REGISTRY.register(MirthStatsCollector())
    REGISTRY.unregister(GC_COLLECTOR)
    REGISTRY.unregister(PLATFORM_COLLECTOR)
    REGISTRY.unregister(PROCESS_COLLECTOR)
    while True:
        # period between collection
        time.sleep(1)