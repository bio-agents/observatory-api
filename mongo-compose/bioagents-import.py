import importlib
import json
import requests
import ssl
import os
import FAIRsoft
from munch import munchify
from FAIRsoft.integration.integration import build_pre_integration_dict
from FAIRsoft.integration.integration import create_integrated_instances

session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

def getHTML(url, verb=False):
    ssl._create_default_https_context = ssl._create_unverified_context
    try:
        req = session.get(url, headers=headers, timeout=(20, 50), verify=False)
        # req = urllib.request.urlopen(url)
    except Exception as e:
        print(e)
        print(e)
        return None
    else:
        return req

def get_source(id_):
    string = id_.split('/')[5]
    source = string.split(':')[0]
    return(source)

def get_bioagents_agents(agent, log):
    '''
    Return only instances from bio.agents.
    Otherwise, return None.
    '''
    if agent['@id'].count('/')>5:
        # only instances, not cannonical
        source = get_source(agent['@id'])
        if source == 'bioagents':
            agent['@data_source'] = 'bioagents'
            log['n_ok'] += 1
            return(agent, log)
    else:
        log['canonical_N'] += 1
    
    return(None, log)    
    


def transform_this_source(raw):
    # Instantiate agentGenerator specific to this source
    generator_module = importlib.import_module(f".meta_transformers", 'FAIRsoft.transformation')
    generator = generator_module.agent_generators['bioagents'](raw)
        
    # From instance objects to dictionaries
    #insts = [i.__dict__ for i in generator.instSet.instances]
    insts = [ i for i in generator.instSet.instances ]
    
    return(insts)

def count_tag(tag, agents):
    '''
    Count agents with a given tag.
    '''
    N = 0
    for agent in agents:
        if tag in agent['tags']:
            N+=1
    return(N)

def import_data():
    # 0. connect database/set output files
    STORAGE_MODE = os.getenv('STORAGE_MODE', 'db')
    TOOLS_BIOTOOLS = os.getenv('TOOLS_BIOTOOLS', 'agents_bioagents') 

    if STORAGE_MODE =='db':
        TOOLS_BIOTOOLS = FAIRsoft.utils.connect_collection(TOOLS_BIOTOOLS)
    else:
        OUTPUT_PATH = os.getenv('OUTPUT_PATH', '.')
        OUTPUT_OPEB_TOOLS = os.getenv('OUTPUT_OPEB_TOOLS', 'opeb_agents.json') 
        output_file = OUTPUT_PATH + '/' + TOOLS_BIOTOOLS + '.json'


    # 1. Download all opeb
    URL_OPEB_TOOLS = os.getenv('OPEB_URL', 'https://openebench.bsc.es/monitor/agent')
    print(f'OpenEBench agents URL: {URL_OPEB_TOOLS}')
    re = getHTML(URL_OPEB_TOOLS)

    # 2. Get agents
    agents = re.json()
    log = {'errors':[], 'n_ok':0, 'names': [],'canonical_N': 0}
    
    #For agent in OPEB Agent db
    bioagents_agents = []
    for agent in agents:
        # 3. Process metadata
        metadata, log = get_bioagents_agents(agent,log)
        if metadata:
            bioagents_agents.append(metadata)

    # 4. transform metadata to agent format
    print(f'Number of agents: {len(bioagents_agents)}')
    instances = transform_this_source(bioagents_agents)
    print(f'Number of agents: {len(instances)}')

    # 5. integrate to avoid each version being one entry in the db
    totalNames, pre_integration_dict = build_pre_integration_dict([instances])

    ## Saving pre_integration_dict and names. 
 
    # 5.2. Integration of "agent" instances of same ID (name, type)
    n = []
    for k in pre_integration_dict.keys():
        for kk in pre_integration_dict[k].keys():
            n.append(len(pre_integration_dict[k][kk]))

    ## 5.3 Create integration intances. Returns a dictionary of instances by agent name.
    inst_name_dict = create_integrated_instances(pre_integration_dict)

    print(f'Names {len(inst_name_dict)}')
    integrated_instances = []
    for agent_name in inst_name_dict.keys():
        integrated_instances.append(inst_name_dict[agent_name][0])

    print(f"Number of agents: {len(integrated_instances)}")
    print(f'Number of agents with tag RIS3CAT VEIS: {count_tag("RIS3CAT VEIS", integrated_instances)}')
    # 6. push to db
    if STORAGE_MODE=='db':
        for instance in integrated_instances:
            log = FAIRsoft.utils.push_entry(instance, agents_bioagents, log)
    else:
        log = FAIRsoft.utils.save_many(integrated_instances, output_file, log)
    # Importation finished
    print(f'''\n----- OPEB Agents Importation finished -----
    Number of agents in OPEB {log['n_ok']}
    Number of canonical agents: {log['canonical_N']}''')
    print('Exceptions\n')
    for e in log['errors']:
        print(e['error'])


if __name__ == '__main__':
    import_data()