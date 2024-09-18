from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.helpers.utils import prepareAgentMetadata, prepareMetadataForEvaluation, prepareListsIds, keep_first_label
from app.helpers.makejson import build_json_ld
from app.helpers.makecff import create_cff
from app.helpers.database import connect_DB

router = APIRouter()

agents_collection, stats = connect_DB()



@router.get('/names_type_labels', tags=["agents"])
async def names_type_labels():
    agents = list(agents_collection.find({'source': {'$ne': ['galaxy_metadata']}}, {
        '_id': 0,
        '@id': 1,
        'label': 1,
        'type': 1,
        'sources_labels': 1,
        'name': 1
    }))
    resp = [keep_first_label(agent) for agent in agents]
    return JSONResponse(content=resp)

@router.get('', tags=["agents"])
async def agent_metadata(name: str = None, type: str = None):
    if not name and not type:
        raise HTTPException(status_code=400, detail="No agent name or type provided")
    agent = agents_collection.find_one({'name': name, 'type': type})
    if agent:
        agent = prepareAgentMetadata(agent)
        agent = prepareListsIds(agent)
        return JSONResponse(content=agent)
    else:
        raise HTTPException(status_code=400, detail="Something went wrong :(")


@router.get('/all', tags=["agents"])
async def get_all_agents():
    try:
        agents = list(agents_collection.find({}))
        for entry in agents:
            entry.pop('_id', None)
        data = {'agents': agents}
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Something went wrong while fetching agent entries: {err}")
    return JSONResponse(content={'message': data, 'code': 'SUCCESS'})


@router.post('/jsonld', tags=["agents"])
async def agent_jsonld(request: Request):
    agent = await request.json()
    agent = agent['data']
    try:
        agent = prepareMetadataForEvaluation(agent)
        agent = build_json_ld(agent)
    except:
        raise HTTPException(status_code=400, detail="Something went wrong when building the JSON-LD :(")
    return JSONResponse(content=agent)

@router.post('/cff', tags=["agents"])
async def agent_cff(request: Request):
    agent = await request.json()
    agent = agent['data']
    try:
        agent = prepareMetadataForEvaluation(agent)
        cff = create_cff(agent)
    except:
        raise HTTPException(status_code=400, detail="Something went wrong when building the CFF :(")
    return JSONResponse(content=cff)
