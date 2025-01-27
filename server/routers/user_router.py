from fastapi import APIRouter,status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from core.api_models import AppUser_API, Location_API, Person_API
from features.user.user_delete import delete_user
from features.user.user_fetch import fetch_all_users, fetch_user_by_id
from features.user.user_insert import insert_user
from features.user.user_net import update_user_password


app_user_router = APIRouter()


@app_user_router.get("/appUser")
def get_all_Users():
    return fetch_all_users()

@app_user_router.get("/appUser/{user_id}")
def get_User_by_id(user_id: int):
    """The selected code snippet is a FastAPI endpoint for fetching a single user from the system. It is defined within the `app_user_router` and is accessible via the GET request method at the "/appUser/{user_id}" endpoint.

The endpoint takes a path parameter `user_id` of type `int`. This parameter is used to identify the user to be fetched.

Inside the function `get_User_by_id`, the `fetch_user_by_id` function is called with the provided `user_id`. This function is responsible for retrieving the user details from the database based on the given `user_id`.

The retrieved user details are then returned as the response of the endpoint. If an error occurs during the retrieval process, an appropriate error response is returned with a status code of 406 (Not Acceptable) and an error message.

Overall, this code snippet demonstrates how to create a FastAPI endpoint for fetching a single user based on the provided `user_id`."""
    res = fetch_user_by_id(user_id)
    return res

@app_user_router.put("/appUser/add")
async def insert_User(user: AppUser_API,person: Person_API=None,location: Location_API=None):
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
        res = await insert_user(user,person,location)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't insert user."}),
    )
    return res


@app_user_router.delete("/appUser/delete")
def delete_User(user: AppUser_API):
    """The selected code snippet is a FastAPI endpoint for deleting a user from the system. It is defined within the app_user_router and is accessible via the DELETE request method at the "/appUser/delete" endpoint."""
    try:
        res = delete_user(user)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't delete user."}),
    )
    return res

@app_user_router.post("/appUser/update")
def update_User(user: AppUser_API,token:str):
    """The selected code snippet is a FastAPI endpoint for deleting a user from the system. It is defined within the app_user_router and is accessible via the update request method at the "/appUser/update" endpoint."""
    try:
        res = update_user_password(user,token)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't delete user."}),
    )
    return res
