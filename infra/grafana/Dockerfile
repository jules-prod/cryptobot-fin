FROM grafana/grafana:11.2.0

USER root
RUN grafana-cli plugins install frser-sqlite-datasource \
    && grafana-cli plugins install yesoreyeram-infinity-datasource
USER grafana
