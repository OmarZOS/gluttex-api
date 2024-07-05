from fastapi import APIRouter,status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from core.api_models import AppUser_API, Location_API, Person_API
from features.user.user_delete import delete_user
from features.user.user_fetch import fetch_all_users, fetch_user_by_id
from features.user.user_insert import insert_user




app_user_router = APIRouter()




@app_user_router.get("/appUser")
def get_all_Users():
    return fetch_all_users()

@app_user_router.get("/appUser/{user_id}")
def get_User_by_id(user_id: int):
    res = fetch_user_by_id(user_id)
    return res

@app_user_router.put("/appUser/add")
def insert_User(user: AppUser_API,person: Person_API=None,location: Location_API=None):
    """
    This function is responsible for inserting a new user into the system.

    Parameters:
    user (AppUser_API): The user object to be inserted.
    person (Person_API, optional): The person object associated with the user. Defaults to None.
    location (Location_API, optional): The location object associated with the user. Defaults to None.

    Returns:
    JSONResponse: A JSON response object containing the result of the insertion operation.
                 If successful, the response will contain the inserted user's details.
                 If an error occurs, the response will contain an error message.

    Raises:
    Exception: If any error occurs during the insertion process.
    """
    try:
        res = insert_user(user,person,location)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't insert user."}),
    )
    return res


@app_user_router.delete("/appUser/delete")
def delete_User(user: AppUser_API):
    try:
        res = delete_user(user)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't delete user."}),
    )
    return res


