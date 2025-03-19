from core.models import AppUser
import storage.wrappers.sql_wrapper as SQLWrapper  

def test_sql_wrapper_insert(db):
    session = SQLWrapper.get_session(db)
    user_data = AppUser() 
    user = session.add_record("users", user_data)
    assert user.id is not None