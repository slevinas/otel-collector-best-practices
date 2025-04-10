# Updated storage layer using PostgreSQL
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db_orm.db import get_db
from api_fastapi.db.models import StoredResource, ApiBenchmarkLog


# --- Store JSON into PostgreSQL ---
async def store_json_db(name: str, data: dict, db: AsyncSession):
    try:
        stmt = select(StoredResource).where(StoredResource.name == name)
        result = await db.execute(stmt)
        existing = result.scalars().first()

        if existing:
            existing.data = data
        else:
            new_entry = StoredResource(name=name, data=data)
            db.add(new_entry)

        await db.commit()
        return {"message": f"Stored JSON under '{name}'", "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Store failed: {str(e)}")


# --- Get JSON or nested key from PostgreSQL ---
from utils.scriptB import get_value_from_resource

async def get_stored_json_db(name: str, key: str | None, db: AsyncSession):
    stmt = select(StoredResource).where(StoredResource.name == name)
    result = await db.execute(stmt)
    resource = result.scalars().first()

    if not resource:
        raise HTTPException(status_code=404, detail=f"Resource '{name}' not found in DB")

    if key:
        try:
            value = get_value_from_resource(key, resource.data)
            return {"name": name, "key": key, "value": value}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Key error: {str(e)}")

    return resource.data


# --- Vector math using PostgreSQL storage ---
async def run_vector_math_db(operation: str, sources: list[str], db: AsyncSession):
    try:
        op = operation.lower()
        if len(sources) < 2:
            raise ValueError("At least two sources are required.")

        stmt = select(StoredResource).where(StoredResource.name.in_(sources))
        result = await db.execute(stmt)
        resources = {r.name: r.data for r in result.scalars()}
        # print(f"zigi from run_vector_math_db the resourses are: {resources}")
        # {'A': {'x': {'value': 5.0}, 'y': {'value': 3.0}},
        #  'B': {'x': {'value': 6.86024533843412}, 'y': {'value': 9.735505361221492}}}

        if len(resources) < len(sources):
            missing = set(sources) - set(resources.keys())
            raise ValueError(f"Missing resources in DB: {missing}")

        base = resources[sources[0]]
        # print(f"zigi from run_vector_math_db the base is: {base}")
        # {'x': {'value': 5.0}, 'y': {'value': 3.0}}
        result = {k: {"value": base[k]["value"]} for k in base}
        # print(f"zigi from run_vector_math_db the result is: {result}")
        # {'x': {'value': 5.0}, 'y': {'value': 3.0}}

        for src in sources[1:]:
            for key in result:
                if key in resources[src] and "value" in resources[src][key]:
                    if op == "add":
                        result[key]["value"] += resources[src][key]["value"]
                    elif op == "subtract":
                        result[key]["value"] -= resources[src][key]["value"]
                    else:
                        raise ValueError("Unsupported operation. Use 'add' or 'subtract'.")

        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Math error: {str(e)}")


# async def save_benchmark_db(name: str, operation: str, sources: list[str], result: dict, elapsed: float, db: AsyncSession):
#     benchmark = Benchmark(
#         name=name,
#         operation=operation,
#         sources=sources,
#         result=result,
#         elapsed=elapsed
#     )
#     db.add(benchmark)
#     await db.commit()



async def run_vector_math_db2(operation: str, sources: list[str], db: AsyncSession):
    print(f"zigi running run_vector_math_db2")
    if operation not in {"add", "subtract"}:
        raise HTTPException(status_code=400, detail=f"Unsupported operation: {operation}")

    # Fetch all source resources
    data_list = []
    for name in sources:
        stmt = select(StoredResource).where(StoredResource.name == name)
        result = await db.execute(stmt)
        resource = result.scalar_one_or_none()
        if not resource:
            raise HTTPException(status_code=404, detail=f"Resource not found: {name}")
        data_list.append(resource.data)

    # Merge keys and perform vector operation
    output = {}
    keys = set().union(*[data.keys() for data in data_list])

    for key in keys:
        try:
            values = [d[key]["value"] for d in data_list]
            if operation == "add":
                result = sum(values)
            elif operation == "subtract":
                result = values[0]
                for v in values[1:]:
                    result -= v
            output[key] = {"value": result}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Math error at key '{key}': {str(e)}")

    return output
