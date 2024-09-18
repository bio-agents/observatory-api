# --------------------------------------------
#      DEPRECATED
# --------------------------------------------


from munch import munchify

from app.helpers.FAIR_indicators import instance


def prepFAIRcomp(instances):
    stdFormats= getFormats(instances)
    return(stdFormats)
    

def getFormats(instances):
    inputs = [a.input for a in instances]
    inputs_ = [a for a in inputs]
    inputsNames = []

    nonSFormats = ['txt', 'text', 'csv', 'tsv', 'tabular', 'xml', 'json', 'nucleotide', 'pdf', 'interval' ]
    for List in inputs_:
        for eachD in List:
            if 'format' in eachD.keys():
                if ' format' not in eachD['format']['term'] and eachD['format']['term'].lstrip() not in nonSFormats:
                    if '(text)' not in eachD['format']['term']:
                        if eachD['format']['term'].lstrip() not in inputsNames:
                            inputsNames.append(eachD['format']['term'].lstrip())
    return(inputsNames)


def convert_dict2instance(agent):
    print(agent.keys())
    if 'version' not in agent.keys():
        agent['version'] = None
    if 'type' not in agent.keys():
        agent['type'] = None
    if 'name' not in agent.keys():
        agent['name'] = None
    NewInst = instance(agent.get('name'), agent.get('type'), agent.get('version'))
    NewInst.__dict__ = munchify(agent)
    NewInst.set_super_type()

    return(NewInst)

def computeFAIR(instances, stdFormats):
    for ins in instances:
        ins.generateFAIRMetrics(stdFormats)
        ins.FAIRscores()


def build_indicators_scores(instances):
    print('Saving indicators and scores')
    out_inst_metrics_scr = []
    for ins in instances:
        dic = { **ins.metrics.__dict__, **ins.scores.__dict__ }
        # name, version, type are needed to identify the instance
        dic['name'] = ins.name
        dic['type'] = ins.type
        dic['version'] = ins.version
        out_inst_metrics_scr.append(dic)

    print("Metrics and scores saved")
    return(out_inst_metrics_scr)   


def computeScores_from_list(agents):
    instances = []

    for agent in agents:
        Inst = convert_dict2instance(agent)
        instances.append(Inst)

    global stdFormats
    stdFormats = prepFAIRcomp(instances)

    print('All dicts converted to instances')
    prepFAIRcomp(instances)

    print('Computing indicators and scores ...')
    computeFAIR(instances, stdFormats)

    print("Building objects of instances' indicators and scores (with instance ID) ...")
    indicators_scores = build_indicators_scores(instances)

    return(indicators_scores)



