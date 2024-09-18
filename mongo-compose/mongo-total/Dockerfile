FROM mongo

#ADD https://observatory.openebench.bsc.es/api/agents /tmp/agents.json
COPY agents-total.json /tmp/agents-total.json
RUN jq '.message.agents' /tmp/agents-total.json  > /tmp/init.json
CMD mongoimport --host localhost --db observatory --collection agents --type json --file /tmp/init.json --jsonArray