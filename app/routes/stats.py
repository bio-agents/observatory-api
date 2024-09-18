from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.helpers.router import make_query

router = APIRouter()

@router.get('/agents/licenses_summary_sunburst', tags=["stats"])
async def licenses_summary_sunburst(request: Request):
    params = request.query_params
    resp = await make_query('licenses_summary_sunburst', params)
    return JSONResponse(content=resp)

@router.get('/agents/licenses_open_source', tags=["stats"])
async def licenses_open_source(request: Request):
    params = request.query_params
    resp = await make_query('licenses_open_source', params)
    return JSONResponse(content=resp)

@router.get('/agents/semantic_versioning', tags=["stats"])
async def semantic_versioning(request: Request):
    params = request.query_params
    resp = await make_query('semantic_versioning', params)
    return JSONResponse(content=resp)

@router.get('/agents/version_control_count', tags=["stats"])
async def version_control_count(request: Request):
    params = request.query_params
    resp = await make_query('version_control_count', params)
    return JSONResponse(content=resp)

@router.get('/agents/version_control_repositories', tags=["stats"])
async def version_control_repositories(request: Request):
    params = request.query_params
    resp = await make_query('version_control_repositories', params)
    return JSONResponse(content=resp)

@router.get('/agents/publications_journals_IF', tags=["stats"])
async def publications_journals_IF(request: Request):
    params = request.query_params
    resp = await make_query('publications_journals_IF', params)
    return JSONResponse(content=resp)

@router.get('/agents/count_per_source', tags=["stats"])
async def counts_per_source(request: Request):
    params = request.query_params
    resp = await make_query('agents_counts_per_source', params)
    return JSONResponse(content=resp)

@router.get('/agents/count_total', tags=["stats"])
async def count_total(request: Request):
    params = request.query_params
    resp = await make_query('agents_count', params)
    return JSONResponse(content=[resp])

@router.get('/agents/features', tags=["stats"])
async def features(request: Request):
    params = request.query_params
    resp = await make_query('features', params)
    return JSONResponse(content=resp)

@router.get('/agents/coverage_sources', tags=["stats"])
async def coverage_sources(request: Request):
    params = request.query_params
    resp = await make_query('coverage_sources', params)
    return JSONResponse(content=resp)

@router.get('/agents/features_cummulative', tags=["stats"])
async def features_cummulative(request: Request):
    params = request.query_params
    resp = await make_query('features_cummulative', params)
    return JSONResponse(content=resp)

@router.get('/agents/distribution_features', tags=["stats"])
async def distribution_features(request: Request):
    params = request.query_params
    resp = await make_query('distribution_features', params)
    return JSONResponse(content=resp)

@router.get('/agents/types_count', tags=["stats"])
async def types_count(request: Request):
    params = request.query_params
    resp = await make_query('types_count', params)
    return JSONResponse(content=resp)

@router.get('/agents/fair_scores_summary', tags=["stats"])
async def fair_scores_summary(request: Request):
    params = request.query_params
    resp = await make_query('FAIR_scores_summary', params)
    return JSONResponse(content=resp)

@router.get('/agents/fair_scores_means', tags=["stats"])
async def fair_scores_means(request: Request):
    params = request.query_params
    resp = await make_query('FAIR_scores_means', params)
    return JSONResponse(content=resp)


