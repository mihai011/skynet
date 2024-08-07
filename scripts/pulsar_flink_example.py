import logging
import sys

from pyflink.common import SimpleStringSchema, WatermarkStrategy
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.pulsar import PulsarSource, PulsarSink, StartCursor, \
    StopCursor, DeliveryGuarantee, TopicRoutingMode

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")

    PULSAR_SQL_CONNECTOR_PATH = 'file:///scripts/flink-sql-connector-pulsar-1.16.0.0.jar'
    SERVICE_URL = 'pulsar://broker:6650'
    ADMIN_URL = 'http://broker:8080'

    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    env.add_jars(PULSAR_SQL_CONNECTOR_PATH, "file:///scripts/flink-shaded-guava-30.1.1-jre-14.0.jar")

    pulsar_source = PulsarSource.builder() \
        .set_service_url(SERVICE_URL) \
        .set_admin_url(ADMIN_URL) \
        .set_topics('ada') \
        .set_start_cursor(StartCursor.latest()) \
        .set_unbounded_stop_cursor(StopCursor.never()) \
        .set_subscription_name('pyflink_subscription') \
        .set_deserialization_schema(SimpleStringSchema()) \
        .set_config('pulsar.source.enableAutoAcknowledgeMessage', True) \
        .set_properties({'pulsar.source.autoCommitCursorInterval': '1000'}) \
        .build()

    ds = env.from_source(source=pulsar_source,
                         watermark_strategy=WatermarkStrategy.for_monotonous_timestamps(),
                         source_name="pulsar source")

    pulsar_sink = PulsarSink.builder() \
        .set_service_url(SERVICE_URL) \
        .set_admin_url(ADMIN_URL) \
        .set_producer_name('pyflink_producer') \
        .set_topics('beta') \
        .set_serialization_schema(SimpleStringSchema()) \
        .set_delivery_guarantee(DeliveryGuarantee.AT_LEAST_ONCE) \
        .set_topic_routing_mode(TopicRoutingMode.ROUND_ROBIN) \
        .set_config('pulsar.producer.maxPendingMessages', 1000) \
        .set_properties({'pulsar.producer.batchingMaxMessages': '100'}) \
        .build()

    ds.sink_to(pulsar_sink).name('pulsar sink')

    env.execute()