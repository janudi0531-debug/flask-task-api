from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import REGISTRY

metrics_instance = None

def setup_metrics(app):
    global metrics_instance
    if metrics_instance is None:
        metrics_instance = PrometheusMetrics(app)
        metrics_instance.info('app_info', 'Flask Task API', version = '1.0.0')
    else:
        metrics_instance.init_app(app)
    return metrics_instance