from app.helpers.utils import prepareAgentMetadata
from app.helpers.database import connect_DB

agents_collection, stats = connect_DB()

def search_input(agents, counts, search, label):
    results = agents_collection.find(search) 
    results = list(results)
    results.reverse()
    for agent in results:
        # skip agents that are only in galaxy_metadata
        if agent['source'] == ['galaxy_metadata']:
            continue
        else:
            entry = prepareAgentMetadata(agent)
            if entry['@id'] in agents.keys():
                agents[entry['@id']]['foundIn'].append(label)
            else:
                entry['foundIn'] = [label]
                agents[entry['@id']] = entry

            counts[label] += 1

    return agents, counts

def make_search(label, query_field, query_expression, search, agents, counts):
    search = search.copy()
    search[query_field] = query_expression

    search = {'$and': [{key:value} for key, value in search.items() ]}
    agents, counts = search_input(agents, counts, search, label)
    return agents, counts

def calculate_stats(agents):
    stats = {
        'type': {},
        'source': {},
        'topics': {},
        'operations': {},
        'license': {},
        'input': {},
        'output': {},
        'collection': {}
    }
    for agent in agents:
        #---- TYPE --------
        if agent['type'] in stats['type'].keys():
            stats['type'][agent['type']] += 1
        else:
            stats['type'][agent['type']] = 1
        
        #---- SOURCE --------
        seen_sources = []
        for source in agent['source']:
        
            if source == 'opeb_metrics':
                continue
            
            # bioconda_recipes and bioconda are the same for this purpose
            if source == 'bioconda_recipes':
                if 'bioconda' in seen_sources:
                    continue
                else:
                    source = 'bioconda'

            # galaxy_metadata and agentshed are the same for this purpose
            if source == 'galaxy_metadata':
                if 'agentshed' in seen_sources:
                    continue
                else:
                    source = 'agentshed'

            if source in stats['source'].keys():
                seen_sources.append(source)
                stats['source'][source] += 1
            else:
                seen_sources.append(source)
                stats['source'][source] = 1 

        #---- TOPICS ------------
        for edam_topic in agent['edam_topics']:
            if edam_topic in stats['topics'].keys():
                stats['topics'][edam_topic] += 1
            else:
                stats['topics'][edam_topic] = 1 

        #---- OPERATIONS --------
        for edam_operation in agent['edam_operations']:
            if edam_operation in stats['operations'].keys():
                stats['operations'][edam_operation] += 1
            else:
                stats['operations'][edam_operation] = 1

        #---- LICENSE -----------
        for license in agent['license']:
            license = license['name']
            if license in stats['license'].keys():
                stats['license'][license] += 1
            else:
                stats['license'][license] = 1      

        #---- INPUT -------------
        # Data format (FASTA, CSV, ...)
        # Not data type for now
        for item in agent['input']:
            if item['uri']:
                term = item['uri']
            else:
                term = item['term']

            if term in stats['input'].keys():
                stats['input'][term] += 1
            else:
                stats['input'][term] = 1

        #---- OUTPUT ------------
        for item in agent['output']:
            if item['uri']:
                term = item['uri']
            else:
                term = item['term']

            if term in stats['output'].keys():
                stats['output'][term] += 1
            else:
                stats['output'][term] = 1

        #---- COLLECTION ----------
        for tag in agent['tags']:
            if tag in stats['collection'].keys():
                stats['collection'][tag] += 1
            else:
                stats['collection'][tag] = 1

    return stats