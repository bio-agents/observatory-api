import re
from funcagents import wraps
import warnings
import time

from app.helpers.EDAM_forFE import EDAMDict


def attribute_check_and_set(instance, key, value, default_name='fairsoft_default_name', default_value=None):
    '''Check if the attribute is set. If it is not, set default attribute to the instance and raise a warning.'''
    if value == 'fairsoft_default':
        warnings.warn(f'Instance {key} not specified. Setting instance.{key} = None')
        setattr(instance, key, None)
    elif value == default_name:
        warnings.warn(f'Instance {key} not specified. Assigning default value "{default_name}"', Warning)
        setattr(instance, key, default_name)
    else:
        setattr(instance, key, value)

def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds')
        return result
    return timeit_wrapper


########
# Agent preparation functions
# These functions prepare the agent metadata to be displayed in the UI
#######

def prepareAgentMetadata(agent):
    '''
    Triggers all the preparation functions sequentially
    '''
    agent.pop('_id')
    # Several fields need processing to be displayed in the UI:
    ## Prepare Labels 
    agent = prepareLabel(agent)

    ## Prepare description
    agent = prepareDescription(agent)
    ## Prepare topics and operations - not needed anymore
    agent = prepareTopicsOperations(agent, 'edam_topics', 'topics')
    agent = prepareTopicsOperations(agent, 'edam_operations', 'operations')
    ## Prepare documentation
    agent = prepareDocumentation(agent)
    ## Prepare authors 
    agent = prepareAuthors(agent)
    ## Prepare license
    agent = prepareLicense(agent)
    ## Prepare publications - not needed anymore
    agent = preparePublications(agent)
    ## Prepare src
    agent = prepareSrc(agent)
    ## Prepare os
    agent = prepareOS(agent)
    ## Prepare input and output data formats - not needed anymore
    agent = prepareDataFormats(agent, 'input')
    agent = prepareDataFormats(agent, 'output')
    # Extract webpages from links
    agent = getWebPage(agent)

    return agent

def prepareLabel(agent):
    '''
    Keep only the label with uppercase letter if it exists
    '''
    def hasUpper(string):
        for letter in string:
        
            # checking for uppercase character and flagging
            if letter.isupper():
                res = True
                return True
        
        return False

    for label in agent['label']:
        if hasUpper(label):
            # put first in labels. LAbels is list to keep backwards compatibility
            agent['label'] = [label]
            break
    
    return agent
    

def prepareTopicsOperations(metadata, field, new_field):
    '''
    Prepares the topics and operations fields of a agent to be displayed in the UI
    field is the field to be processed (edam_topics or edam_operations)
    Example of processed field:
    [
        {
            "vocabulary": "EDAM",
            "term": "Topic",
            "uri": "http://edamontology.org/topic_0003"
        },
        ...
    ]
    
    '''
    items = metadata[field]
    new_items = []
    # look up for each item in the list the corresponding label
    for item in items:
        term = EDAMDict.get(item)
        if item:
            item = {
                'vocabulary': 'EDAM',
                'term': term,
                'uri': item
            }
            new_items.append(item)
    
    metadata[new_field] = new_items
    return metadata

def prepareDocumentation(metadata):
    '''
    Prepares the documentation field of a agent to be displayed in the UI
    Example of processed field:
    [
        {
            "type": "documentation",
            "url": "https://bio.agents/api/agent/blast2go/docs/1.0.0"
        },
        ...
    ]
    
    '''
    def match_url(string):
        # either http or https
        pattern = re.compile(r'https?://\S+')
        if pattern.match(string):
            return True
        else:
            return False

    def clean_documentation(documentation):
        '''
        Removes the documentation items that are not urls
        '''
        new_documentation = []
        for item in documentation:
            new_item = []
            if type(item[1])==str:
                if match_url(item[1]):
                    if item[0] == 'documentation':
                        new_item.append('general')
                    else:
                        new_item.append(item[0])
                    new_item.append(item[1])
                    new_documentation.append(new_item)

        return new_documentation

    items = clean_documentation(metadata['documentation'])
    new_items = []
    # look up for each item in the list the corresponding label
    for item in items:
        item = {
            'type': item[0],
            'url': item[1]
        }
        new_items.append(item)
    
    metadata['documentation'] = new_items
    return metadata


def prepareDataFormats(metadata, field):
    '''
    Prepares the input and output field of a agent to be displayed in the UI
    Example of processed field:
    [
        {   "vocabulary": "EDAM",
            "term": "Sequence format",
            "uri": "http://edamontology.org/format_1929",
            datatype: {
                "vocabulary": "EDAM",
                "term": "Sequence",
                "uri": "http://edamontology.org/data_0006"
            }
        },
        ...
    ]
    
    '''
    items = metadata[field]
    new_items = []
    # look up for each item in the list the corresponding label
    #print(items)
    for item in items:
        if 'datatype' in item:
            datatype = {
                'vocabulary': 'EDAM',
                'term': EDAMDict[item['datatype']],
                'uri': item['datatype']
            }
        else:
            datatype = {}

        # fix this ugly hack later
        if 'format' in item:
            format = {
                'vocabulary': '',
                'term': item['format']['term'],
                'uri': item['format']['uri'],
            }
            new_items.append(format)
        else:
            for format in item['formats']:
                if datatype:
                    format = {
                        'vocabulary': 'EDAM',
                        'term': EDAMDict[format],
                        'uri': format,
                        'datatype': datatype
                    }
                else:
                    format = {
                        'vocabulary': 'EDAM',
                        'term': EDAMDict[format],
                        'uri': format
                    }
                new_items.append(format)
    
    metadata[field] = new_items
    
    return metadata

def prepareListsIds(metadata):
    '''
    Add ids to a list of terms. 
    The ids are needed for v-for loops to keep proper track of items.
    See: https://stackoverflow.com/questions/44531510/why-not-always-use-the-index-as-the-key-in-a-vue-js-for-loop/75175749#75175749 
    fields: agent metadata fields that we need to add ids to.
    From:
    [
        term1,
        term2,
        ...
    ]
    To:
    [
        { term: term1, id: id1 },
        { term: term2, id: id2 },
        ...
    ]
    '''

    fields = [
        'edam_topics',
        'edam_operations',
        'documentation',
        'description',
        'webpage',
        'license',
        'src',
        'links',
        'topics',
        'operations',
        'input',
        'output',
        'repository',
        'dependencies',
        'os',
        'authors',
        'publication'
    ]

    #print(metadata)
    for field in fields:
        #print(f'Adding ids to field: {field}')
        new_list = [] 
        i=0
        if metadata.get(field):
            for item in metadata.get(field):
                new_item ={
                    'term': item,
                    'id': i
                }
                new_list.append(new_item)
                i+=1

            metadata[field] = new_list
    
    return metadata


def getWebPage(metadata):
    '''
    Returns the webpage of a agent
    '''
    webpages= set()
    new_links= set()
    for link in metadata['links']:
        x = re.search("^(.*)(\.)(rar|bz2|tar|gz|zip|bz|json|txt|js|py|md)$", link)
        if x:
            new_links.add(link)
        else:
            webpages.add(link)
    
    metadata['webpage'] = list(webpages)
    metadata['links'] = list(new_links)

    return metadata

def clean_brakets(string):
    '''
    Remove anything between {}, [], or <>, or after {, [, <
    '''
    def clena_after_braket(string):
        '''
        Remove anything between {}, [], or <>
        '''
        pattern = re.compile(r'\{.*|\[.*|\(.*|\<.*')
        return re.sub(pattern, '', string)

    def clean_between_brakets(string):
        '''
        Remove anything between {, [, <
        '''
        pattern = re.compile(r'\{.*?\}|\[.*?\]|\(.*?\)|\<.*?\>')
        return re.sub(pattern, '', string)

    def clean_before_braket(string):
        '''
        Remove anything before }, ], or >
        '''
        pattern = re.compile(r'.*?\}.*?|.*?\].*?|.*?\>.*?')
        return re.sub(pattern, '', string)


    string = clean_between_brakets(string)
    string = clena_after_braket(string)
    string = clean_before_braket(string)

    return string

def clean_doctor(string):
    '''
    remove title at the begining of the string
    '''
    pattern = re.compile(r'^Dr\.|Dr |Dr\. |Dr')
    return re.sub(pattern, '', string)

def keep_after_code(string):
    '''
    Remove anything before code and others
    '''
    if 'initial R code' in string:
        return ''
    if 'contact form' in string:
        return ''
    else:
        pattern = re.compile(r'.*?code')
        string = re.sub(pattern, '', string)
        pattern = re.compile(r'.*?Code')
        string = re.sub(pattern, '', string)
        pattern = re.compile(r'.*?from')
        string = re.sub(pattern, '', string)
        return re.sub(pattern, '', string)

def clean_first_end_parenthesis(string):
    if string[0] == '(' and string[-1] == ')':
        string = string[1:]
        string = string[:-1]

    return string

def clean_spaces(string):
    '''
    Clean spaces around the string
    '''
    return string.strip()


def classify_person_organization(string):
    '''
    tokenize the string
    if any of the words in the string is in the list of keywords
    then it is an institution
    otherwise it is a person
    '''
    inst_keywords = [
        'university',
        'université',
        'universidad',
        'universidade',
        'università',
        'universität',
        'institut',
        'institute',
        'college',
        'school',
        'department',
        'laboratory',
        'laboratoire',
        'lab',
        'center',
        'centre',
        'research',
        'researcher',
        'researchers',
        'group',
        'support',
        'foundation',
        'company',
        'corporation',
        'team',
        'helpdesk',
        'service',
        'platform',
        'program',
        'programme',
        'community'
    ]
    words = string.split()
    for word in words:
        if word.lower() in inst_keywords:
            return 'organization'
    return 'person'

def clean_long(string):
    if len(string.split()) >= 5:
        return ''
    else:
        return string


def build_organization(string):
    return {
        'type': 'organization',
        'name': string,
        'email': '',
        'maintainer': False
        }

def build_person(string):
    '''
    Extract first and last name from a string
    '''
    if string:
        return {
            'type': 'person' ,
            'name': string, 
            'email': '',
            'maintainer': False
            }
    else:
        return ''
        


def build_authors(authors):
    '''
    Build a list of authors
    '''
    new_authors = []
    seen_authors = set()
    for author in authors:
        name = clean_first_end_parenthesis(author)
        name = clean_brakets(name)
        name = clean_doctor(name)
        name = keep_after_code(name)
        name = clean_spaces(name)
        if name in seen_authors:
            continue
        else:
            seen_authors.add(name)
            classification = classify_person_organization(name)
            if classification == 'person':
                if name:
                    name = clean_long(name)
                    person = build_person(name)
                    new_authors.append(person)

            else:
                organization = build_organization(name)
                new_authors.append(organization)

    return new_authors

def prepareAuthors(agent):
    '''
    {
        "name": "name1",
        "email": "email1",
        "type": "person/organization",
        "maintainer": "true/false"
    }
    '''
    authors = build_authors(agent['authors'])    
    agent['authors'] = authors

    return agent
    


def prepareLicense(agent):
    '''
    {
        "name": "name1",
        "url": "url1"
    }
    '''
    licenses_set= set(agent['license'])
    agent['license'] = list(licenses_set)

    def remove_file_LICENSE(license):
        z = re.match("(.*)\s?\+\s?file\s?LICENSE", license)
        if z:
            license = z.groups(0)[0]
        if 'file' in license:
            license = ''
        return license
    
    new_licenses = []
    for license in agent['license']:
        new_lic = remove_file_LICENSE(license)
        if new_lic:
            new_license = {
                'name': new_lic,
                'url': ''
            }
            new_licenses.append(new_license)
    
    agent['license'] = new_licenses
    return agent

def prepareDescription(agent):
    
    description = set(agent['description'])
    agent['description'] = list(description)
    # return longest description
    longest_description = ''
    for desc in agent['description']:
        if len(desc) > len(longest_description):
            longest_description = desc
    
    # First letter must be uppercase
    longest_description = longest_description.capitalize()

    # Period at the end
    if longest_description:
        if longest_description[-1] != '.':
            longest_description += '.'

    # as a list for backwards compatibility
    agent['description'] = [longest_description]
    
    return agent

def cleanEmptyPublications(publications):
    new_pubs = []
    for pub in publications:
        new_pub = {k: v for k, v in pub.items() if v}
        if new_pub:
            new_pubs.append(new_pub)
    
    return new_pubs

def preparePublications(agent):
    '''
    Merge publications that share ids or title
    '''
    identifiers = ['title', 'pmcid', 'pmid', 'doi']

    def indices(lst, item):
       return [i for i, x in enumerate(lst) if x == item]

    def stripPoints(ids):
        '''
        remove final points from ids (necessary specially in titles)
        '''
        new_ids = []
        for id_ in ids:
            if id_!= None:
                new_ids.append(id_.rstrip('.'))
            else:
                new_ids.append(id_)

        return new_ids
    
    def capitalizeDOIs(ids):
        '''
        capitalize ids
        '''
        new_ids = []
        for id_ in ids:
            if id_!= None:
                new_ids.append(id_.upper())
            else:
                new_ids.append(id_)
        return new_ids

    def removeTags(titles):
        '''
        remove tags from titles
        '''
        new_titles = []
        for title in titles:
            if title != None:
                pattern = re.compile(r'(<.*?>)')
                new_title = re.sub(pattern, '', title)
                new_titles.append(new_title)
            else:
                new_titles.append(title)
        return new_titles

    def merge_by_id(publications, id_):
        seen_ids = []
        ids = [pub.get(id_) for pub in publications]
        ids = stripPoints(ids)
        if id_ == 'doi':
            ids = capitalizeDOIs(ids)
        if id_ == 'title':
            ids = removeTags(ids)

        new_publications = []

        # get indexes of repeated ids
        for a in range(len(ids)):
            id =  ids[a]
            if id != None:
                if id in seen_ids:
                    continue
                else:
                    seen_ids.append(id)
                    indexes = indices(ids, id)
                    new_publication = {}
                    # merge repeated publications by pairs

                    if len(indexes) > 1:
                        # merge needed
                        for i in indexes:
                            new_publication = {**new_publication, **publications[i]}
                                                
                        # merged publications
                        new_publications.append(new_publication)
                    else:
                        # no possible merge. Append publication as it is
                        index = indexes[0]
                        new_publications.append(publications[index])

            else:
                new_publications.append(publications[a])

        return new_publications
    
    publications = cleanEmptyPublications(agent['publication'])
    try:
        for id_ in identifiers:
            publications  = merge_by_id(publications, id_)
        
        for pub in publications:
            if pub.get('title'):
                pub['title'] = pub['title'].rstrip('.')
                pattern = re.compile(r'(<.*?>)')
                pub['title'] = re.sub(pattern, '', pub['title'])

        
        agent['publication'] = publications

    except Exception as e:
        print('Error merging publications')
        print(e)
    else:
        pass
    
    return agent


def prepareSrc(agent):
    #print(agent['src'])
    links=set(agent['src'])
    agent['src'] = list(links)
    return agent


def prepareOS(agent):
    new_os = []
    for os in agent['os']:
        if os == 'Mac':
            new_os.append('macOS')
        else:
            new_os.append(os)
    
    agent['os'] = new_os
    return agent


################
# Prepare metadata for evaluation
################

def prepareMetadataForEvaluation(metadata):
    '''
    Reverts the kind of processing done in prepareListsIds
    From:
    [
        { term: term1, id: id1 },
        { term: term2, id: id2 },
        ...
    ] 
    
    To:
    [
        term1,
        term2,
        ...
    ]
    '''

    fields = [
        'edam_topics',
        'edam_operations',
        'documentation',
        'description',
        'license',
        'src',
        'links',
        'input',
        'output',
        'repository',
        'dependencies',
        'os',
        'authors',
        'publication',
        'topics', # added by prepareTopicsOperations
        'operations', # added by prepareTopicsOperations
        'webpage' # added by getWebPage
    ]

    for field in fields:
        print('preparing field: ', field)
        new_list = [] 
        for item in metadata[field]:
            new_item = item['term']
            new_list.append(new_item)
        
        metadata[field] = new_list

    return metadata


################
# Prepare name-type-label
################

def keep_first_label(agent):
    '''
    Processes a agent to turn a list of labels into a single label (index=0)
    '''
    agent['label'] = agent['label'][0]
    
    return agent


##############
# sources_labels
##############

def find_github_repo(link):
    regex = re.compile(r'(http(s)?:\/\/)?(www\.)?github\.com\/[A-Za-z0-9_-]+\/[A-Za-z0-9_-]+')
    x = re.search(regex, link)
    if x:
        return x.group(0)
    else:
        return None

def find_bioconductor_link(link):
    regex = re.compile(r'(http(s)?:\/\/)?(www\.)?bioconductor\.org\/packages\/[A-Za-z0-9_-]+\/bioc\/html\/[A-Za-z0-9_-]+')
    x = re.search(regex, link)
    if x:
        return x.group(0) + '.html'
    else:
        return None

def find_bitbucket_repo(link):
    '''
    Find Bitbuket repository in URL string
    '''
    regex = re.compile(r'(http(s)?:\/\/)?(www\.)?bitbucket\.org\/[A-Za-z0-9_-]+\/[A-Za-z0-9_-]+')
    x = re.search(regex, link)
    if x:
        return x.group(0)
    else:
        return None

def find_galaxy_instance(link):
    '''
    Find Galaxy instance in URL string
    '''
    regex = re.compile(r'(http(s)?:\/\/)?(www\.)?usegalaxy\.eu')
    x = re.search(regex, link)
    if x:
        return x.group(0)
    else:
        return None

def find_galaxyagentshed_link(link):
    '''
    Find Galaxy agentshed in URL string
    '''
    regex = re.compile(r'(http(s)?:\/\/)?(www\.)?agentshed\.galaxyproject\.org')
    x = re.search(regex, link)
    if x:
        return x.group(0)
    else:
        return None



def prepare_sources_labels(agent):
    '''
    {
        "bioagents" : URL,
        "bioconda" : URL,
        "biocontainers" : URL,
        "galaxy" : URL,
        "agentshed" : URL,
        "bioconductor" : URL,
        "sourceforge" : URL,
        "github" : URL,
        "bitbucket" : URL,
    }
    '''
    sources_labels = {}
    remain_sources = agent['source'].copy()

    if 'opeb_metrics' in remain_sources:
        remain_sources.remove('opeb_metrics')

    if 'bioagents' in agent['source']:
        sources_labels['bioagents'] = f'https://bio.agents/{agent["name"]}'
        remain_sources.remove('bioagents')

    if 'bioconda' in agent['source'] or 'bioconda_recipes' in agent['source']:
        sources_labels['bioconda'] = f'https://anaconda.org/bioconda/{agent["name"]}'
        if 'bioconda_recipes' in agent['source']:
            remain_sources.remove('bioconda_recipes')
        if 'bioconda' in agent['source']:
            remain_sources.remove('bioconda')

    if 'bioconductor' in agent['source']:
        sources_labels['bioconductor'] = f'https://bioconductor.org/packages/release/bioc/html/{agent["name"]}.html'
        remain_sources.remove('bioconductor')
    
    if 'sourceforge' in agent['source']:
        sources_labels['sourceforge'] = f'https://sourceforge.net/projects/{agent["name"]}'
        remain_sources.remove('sourceforge')
    
    if 'agentshed' in agent['source']:
        sources_labels['agentshed'] = f'https://agentshed.g2.bx.psu.edu/repository'
        remain_sources.remove('agentshed')

    if 'galaxy_metadata' in remain_sources:
        sources_labels['agentshed'] = f'https://agentshed.g2.bx.psu.edu/repository'
        remain_sources.append('galaxy')
        remain_sources.remove('galaxy_metadata')
    
    if 'galaxy' in agent['source']:
        sources_labels['galaxy'] = 'https://usegalaxy.eu/'
        remain_sources.remove('galaxy')


    for link in agent['links']:
        foundLink = False
        while not foundLink:
            # bioconda
            # some agents have bioconductor in name in some sources like bioconda
            if f'bioconductor-{agent["name"]}' in link:
                sources_labels['bioconda'] = f'https://anaconda.org/bioconda/bioconductor-{agent["name"]}'

            # github
            github_repo = find_github_repo(link)
            if github_repo:
                sources_labels['github'] = github_repo
                foundLink = True
                if 'github' in remain_sources:
                    remain_sources.remove('github')
            
            # bioconductor
            bioconductor_link = find_bioconductor_link(link)
            if bioconductor_link:
                sources_labels['bioconductor'] = bioconductor_link
                foundLink = True
                if 'bioconductor' in remain_sources:
                    remain_sources.remove('bioconductor')
            
            # bitbucket 
            bitbucket_repo = find_bitbucket_repo(link)
            if bitbucket_repo:
                sources_labels['bitbucket'] = bitbucket_repo
                foundLink = True
                if 'bitbucket' in remain_sources:
                    remain_sources.remove('bitbucket')

            # galaxy
            galaxy_instance = find_galaxy_instance(link)
            if galaxy_instance:
                sources_labels['galaxy'] = galaxy_instance
                foundLink = True
                if 'galaxy' in remain_sources:
                    remain_sources.remove('galaxy')

            # agentshed
            galaxyagentshed_link = find_galaxyagentshed_link(link)
            if galaxyagentshed_link:
                sources_labels['agentshed'] = galaxyagentshed_link
                foundLink = True
                if 'agentshed' in remain_sources:
                    remain_sources.remove('agentshed')

            foundLink = True

    for source in remain_sources:
        sources_labels[source] = ''

    agent['sources_labels'] = sources_labels
    return(agent)



################
# Database connection
################

