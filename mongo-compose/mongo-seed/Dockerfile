FROM mongo

COPY agents-bioagents.json /agents-bioagents.json
CMD mongoimport --host localhost --db observatory --collection bioagents-agents --type json --file /agents-bioagents.json --jsonArray