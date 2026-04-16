# SKILL: API Design & REST Patterns

**Purpose**: Guidelines for designing FastAPI endpoints with proper error handling, pagination, authentication, and documentation.

**Used for**: Creating new routers, designing RESTful endpoints, implementing pagination, error handling, OpenAPI documentation.

---

## Endpoint Template

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from uuid import UUID
from app.core.deps import get_current_user, get_current_tenant
from app.models.user import User
from app.services.resource_service import ResourceService
from app.schemas.resource import ResourceCreate, ResourceUpdate, ResourceResponse

router = APIRouter(prefix="/resources", tags=["resources"])

# === CREATE ===
@router.post(
    "",
    response_model=ResourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create resource",
    description="Create a new resource for the current tenant"
)
async def create_resource(
    data: ResourceCreate,
    user: User = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
    service: ResourceService = Depends(get_resource_service),
):
    """
    Create a new resource.
    
    **Required fields:**
    - `name`: Resource name (max 255 chars)
    
    **Returns:**
    - Resource object with ID, created_at, etc.
    
    **Errors:**
    - 400: Invalid input
    - 409: Duplicate resource
    - 429: Quota exceeded
    """
    try:
        resource = await service.create(tenant_id, data)
        return resource
    except QuotaExceededError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Quota exceeded for this plan"
        )

# === LIST (Paginated) ===
@router.get(
    "",
    response_model=PaginatedResponse[ResourceResponse],
    summary="List resources",
    description="Retrieve paginated list of resources for current tenant"
)
async def list_resources(
    user: User = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    service: ResourceService = Depends(get_resource_service),
):
    """
    **Query Parameters:**
    - `page`: Page number (default: 1)
    - `per_page`: Items per page (default: 10, max: 100)
    - `status`: Filter by status (optional)
    
    **Returns:**
    - Paginated response with `items`, `total`, `page`, `per_page`
    """
    items, total = await service.list(
        tenant_id,
        page=page,
        per_page=per_page,
        status=status
    )
    
    return PaginatedResponse[ResourceResponse](
        items=items,
        total=total,
        page=page,
        per_page=per_page
    )

# === GET (Detail) ===
@router.get(
    "/{resource_id}",
    response_model=ResourceResponse,
    summary="Get resource",
    description="Retrieve a specific resource by ID"
)
async def get_resource(
    resource_id: UUID,
    user: User = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
    service: ResourceService = Depends(get_resource_service),
):
    """
    **Path Parameters:**
    - `resource_id`: Resource UUID
    
    **Returns:**
    - Complete resource object
    
    **Errors:**
    - 404: Resource not found
    """
    resource = await service.get(tenant_id, resource_id)
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource {resource_id} not found"
        )
    
    return resource

# === UPDATE ===
@router.patch(
    "/{resource_id}",
    response_model=ResourceResponse,
    summary="Update resource",
    description="Partially update a resource"
)
async def update_resource(
    resource_id: UUID,
    data: ResourceUpdate,
    user: User = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
    service: ResourceService = Depends(get_resource_service),
):
    """
    **Note:** PATCH allows partial updates (only provided fields are updated).
    """
    resource = await service.update(tenant_id, resource_id, data)
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource {resource_id} not found"
        )
    
    return resource

# === DELETE (Soft) ===
@router.delete(
    "/{resource_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete resource",
    description="Soft-delete a resource (can be restored)"
)
async def delete_resource(
    resource_id: UUID,
    user: User = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
    service: ResourceService = Depends(get_resource_service),
):
    """
    Soft-deletes the resource (sets `deletado_em` timestamp).
    """
    success = await service.delete(tenant_id, resource_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource {resource_id} not found"
        )
```

---

## HTTP Status Codes

| Code | Method | Use Case |
|------|--------|----------|
| **200** | GET, PATCH, PUT | Success (return data) |
| **201** | POST | Resource created |
| **204** | DELETE | Success (no body) |
| **400** | Any | Client error (invalid input) |
| **401** | Any | Unauthorized (missing/invalid token) |
| **403** | Any | Forbidden (authorized but access denied) |
| **404** | Any | Not found |
| **409** | POST, PUT | Conflict (duplicate, constraint) |
| **422** | Any | Validation error (Pydantic) |
| **429** | Any | Too many requests (rate limit) |
| **500** | Any | Server error (bug) |

---

## Pagination Pattern

### Schema
```python
from typing import Generic, List, TypeVar

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int
    
    @property
    def total_pages(self) -> int:
        return (self.total + self.per_page - 1) // self.per_page
```

### Usage
```python
@router.get("/items", response_model=PaginatedResponse[ItemResponse])
async def list_items(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
):
    items, total = await service.list_paginated(page, per_page)
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page
    )
```

---

## Error Handling Pattern

### Standard Error Response
```python
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    error: str
    detail: str
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Usage in endpoint
raise HTTPException(
    status_code=400,
    detail="Invalid input: name must be at least 3 characters"
)
```

### Global Exception Handler
```python
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "status_code": 422
        }
    )
```

---

## Authentication & Authorization Pattern

### Require Authentication
```python
@router.get("/protected")
async def protected_endpoint(
    user: User = Depends(get_current_user),
):
    return {"user_id": user.id}
```

### Require Specific Role
```python
@router.delete("/admin-only")
async def admin_endpoint(
    user: User = Depends(require_role("admin")),
):
    return {"message": "Admin-only action"}
```

### Multi-Tenant Isolation
```python
@router.get("/my-resources")
async def list_my_resources(
    user: User = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),  # ← Injected!
    service: ResourceService = Depends(...)
):
    # Service automatically filters by tenant_id
    return await service.list(tenant_id)
```

---

## Schema Design

### Input Schema (Create)
```python
class ResourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    status: ResourceStatus = Field(default=ResourceStatus.ACTIVE)
```

### Output Schema (Response)
```python
class ResourceResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    status: ResourceStatus
    criado_em: datetime
    atualizado_em: datetime
    
    # Don't expose sensitive fields!
    # chave_secreta_enc: bytes  ← NEVER include
    
    model_config = ConfigDict(from_attributes=True)
```

### Update Schema (Partial)
```python
class ResourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[ResourceStatus] = None
```

---

## Query Filtering

### Pattern: Safe Filter Parameters
```python
@router.get("/resources")
async def list_resources(
    tenant_id: UUID = Depends(get_current_tenant),
    status: Optional[str] = Query(
        None,
        description="Filter by status",
        pattern="^(active|inactive|archived)$"  # Whitelist values
    ),
    created_after: Optional[datetime] = Query(
        None,
        description="Created after date"
    ),
    created_before: Optional[datetime] = Query(
        None,
        description="Created before date"
    ),
):
    """Filter with validation to prevent injection."""
    filters = {}
    if status:
        filters["status"] = status
    if created_after:
        filters["created_after"] = created_after
    if created_before:
        filters["created_before"] = created_before
    
    return await service.list_filtered(tenant_id, **filters)
```

---

## OpenAPI Documentation

### Enrich Endpoint with Metadata
```python
@router.post(
    "/resources",
    response_model=ResourceResponse,
    status_code=201,
    summary="Create resource",
    description="Create a new resource in the current tenant",
    responses={
        201: {"description": "Resource created successfully"},
        400: {"description": "Invalid input"},
        409: {"description": "Duplicate resource name"},
        429: {"description": "Quota exceeded"}
    }
)
async def create_resource(data: ResourceCreate):
    """
    Create a new resource.
    
    **Business Logic:**
    - Validates name uniqueness per tenant
    - Checks quota limit for current plan
    - Encrypts sensitive fields before storage
    
    **Authorization:**
    - User must be authenticated
    - User must have admin/editor role in tenant
    """
    ...
```

---

## Common Mistakes ⚠️

❌ **Mistake 1**: No multi-tenant filtering
```python
# BAD
@router.get("/resources")
async def list_resources():
    return await db.query(Resource).all()  # Returns ALL tenants' data!

# GOOD
@router.get("/resources")
async def list_resources(tenant_id: UUID = Depends(get_current_tenant)):
    return await service.list(tenant_id)
```

❌ **Mistake 2**: Exposing encrypted fields in response
```python
# BAD
class ResourceResponse(BaseModel):
    chave_secreta_enc: bytes  # ← Exposes encrypted data

# GOOD
class ResourceResponse(BaseModel):
    # Omit encrypted fields, or decrypt if necessary
    pass
```

❌ **Mistake 3**: No pagination for large lists
```python
# BAD
@router.get("/items")
async def list_items():
    return await db.query(Item).all()  # Returns millions of rows!

# GOOD
@router.get("/items")
async def list_items(page: int = Query(1), per_page: int = Query(10)):
    return await service.list_paginated(page, per_page)
```

❌ **Mistake 4**: Hard-coded limits instead of plan-based
```python
# BAD
if count > 100:  # ← Hard-coded limit
    raise Error("Limit reached")

# GOOD
plan = get_tenant_plan(tenant_id)
if count > plan.resource_limit:  # ← Plan-based
    raise Error("Quota exceeded")
```

---

## Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic v2 Guide](https://docs.pydantic.dev/latest/)
- [REST API Best Practices](https://restfulapi.net/)

---

**Last Updated**: April 15, 2026  
**Status**: Active
