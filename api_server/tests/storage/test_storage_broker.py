# # tests/storage/test_storage_broker.py (fixed version)

# import pytest
# from unittest.mock import Mock, patch, MagicMock
# from typing import Dict, Any, List
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Column, Integer, String
# from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# from storage.storage_broker import (
#     StorageError,
#     _handle_storage_exception,
#     get_engine_with_retry,
#     insert_record,
#     get,
#     count,
#     delete_record,
#     update_record,
#     delete_record_by_id,
#     search_records,
#     search_by_filter,
#     validate_table_name,
#     validate_pagination
# )
# from core.exceptions.handler import APIException
# from core.messages.error_codes import ErrorCode


# # ==================== SQLAlchemy Model for Testing ====================

# Base = declarative_base()


# class TestModel(Base):
#     """Proper SQLAlchemy model for testing"""
#     __tablename__ = "test_table"
    
#     id = Column(Integer, primary_key=True)
#     name = Column(String(100))
#     description = Column(String(200))


# # ==================== Test Fixtures ====================

# @pytest.fixture
# def mock_engine():
#     """Mock database engine with proper context manager support"""
#     engine = MagicMock()
    
#     # Create a mock connection
#     mock_connection = MagicMock()
#     mock_connection.execute.return_value = None
    
#     # Create a mock context manager that returns the connection
#     mock_context = MagicMock()
#     mock_context.__enter__.return_value = mock_connection
#     mock_context.__exit__.return_value = None
    
#     # Set up the engine's connect method to return the context manager
#     engine.connect.return_value = mock_context
    
#     return engine


# @pytest.fixture
# def mock_record():
#     """Mock database record as a proper model instance"""
#     record = TestModel(id=1, name="Test Record", description="Test Description")
#     return record


# @pytest.fixture
# def mock_records():
#     """Mock list of database records"""
#     return [
#         TestModel(id=1, name="Record 1", description="Description 1"),
#         TestModel(id=2, name="Record 2", description="Description 2"),
#         TestModel(id=3, name="Record 3", description="Description 3"),
#     ]


# # ==================== Exception Handler Tests ====================

# class TestExceptionHandler:
#     """Test the _handle_storage_exception function"""
    
#     def test_handle_storage_error(self):
#         """Test handling of StorageError"""
#         error = StorageError("Test storage error")
        
#         with pytest.raises(APIException) as exc_info:
#             _handle_storage_exception(error, "test_operation", key="value")
        
#         assert exc_info.value.status_code == 400
#         assert exc_info.value.error_code == ErrorCode.DATABASE_ERROR
#         assert "Test storage error" in exc_info.value.message
    
#     def test_handle_integrity_error(self):
#         """Test handling of integrity error"""
#         error = Exception("Duplicate entry 'test@example.com' for key 'email'")
        
#         with pytest.raises(APIException) as exc_info:
#             _handle_storage_exception(error, "insert_record", table="users")
        
#         assert exc_info.value.status_code == 417
#         assert exc_info.value.error_code == ErrorCode.INTEGRITY_ERROR
#         assert "integrity constraint violated" in exc_info.value.message.lower()
    
#     def test_handle_not_found_error(self):
#         """Test handling of not found error"""
#         error = Exception("Record with id 123 not found")
        
#         with pytest.raises(APIException) as exc_info:
#             _handle_storage_exception(error, "get_record", record_id=123)
        
#         assert exc_info.value.status_code == 404
#         assert exc_info.value.error_code == ErrorCode.DATA_ERROR
#         assert "Record not found" in exc_info.value.message
    
#     def test_handle_generic_error(self):
#         """Test handling of generic error"""
#         error = Exception("Some unexpected database error")
        
#         with pytest.raises(APIException) as exc_info:
#             _handle_storage_exception(error, "update_record", table="products")
        
#         assert exc_info.value.status_code == 500
#         assert exc_info.value.error_code == ErrorCode.DATABASE_ERROR
#         assert "Database operation failed" in exc_info.value.message


# # ==================== Engine Tests ====================

# class TestEngine:
#     """Test database engine functions"""
    
#     @patch('storage.storage_broker.medicom_store.get_engine')
#     def test_get_engine_with_retry_success(self, mock_get_engine, mock_engine):
#         """Test successful engine retrieval"""
#         mock_get_engine.return_value = mock_engine
        
#         result = get_engine_with_retry("sqlite:///test.db", retry_count=1)
        
#         assert result == mock_engine
#         mock_get_engine.assert_called_once()
    
#     @patch('storage.storage_broker.medicom_store.get_engine')
#     def test_get_engine_with_retry_failure(self, mock_get_engine):
#         """Test engine retrieval failure after retries"""
#         mock_get_engine.side_effect = Exception("Connection failed")
        
#         with pytest.raises(APIException) as exc_info:
#             get_engine_with_retry("sqlite:///test.db", retry_count=2)
        
#         assert exc_info.value.status_code == 500
#         assert mock_get_engine.call_count == 2
    
#     @patch('storage.storage_broker.medicom_store.get_engine')
#     def test_get_engine_connection_test_failure(self, mock_get_engine, mock_engine):
#         """Test engine retrieval when connection test fails"""
#         mock_get_engine.return_value = mock_engine
#         mock_engine.connect.side_effect = Exception("Connection test failed")
        
#         with pytest.raises(APIException) as exc_info:
#             get_engine_with_retry("sqlite:///test.db", retry_count=1)
        
#         assert exc_info.value.status_code == 500


# # ==================== Insert Record Tests ====================

# class TestInsertRecord:
#     """Test insert_record function"""
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     @patch('storage.storage_broker.medicom_store.add_record')
#     def test_insert_record_success(self, mock_add_record, mock_get_engine, mock_record, mock_engine):
#         """Test successful record insertion"""
#         mock_get_engine.return_value = mock_engine
#         mock_add_record.return_value = mock_record
        
#         result = insert_record(mock_record)
        
#         assert result == mock_record
#         mock_add_record.assert_called_once_with(mock_engine, mock_record)
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     def test_insert_record_engine_failure(self, mock_get_engine, mock_record):
#         """Test insertion when engine retrieval fails"""
#         mock_get_engine.return_value = None
        
#         with pytest.raises(APIException) as exc_info:
#             insert_record(mock_record)
        
#         assert exc_info.value.status_code == 400
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     @patch('storage.storage_broker.medicom_store.add_record')
#     def test_insert_record_integrity_error(self, mock_add_record, mock_get_engine, mock_record, mock_engine):
#         """Test insertion with integrity error"""
#         mock_get_engine.return_value = mock_engine
#         mock_add_record.side_effect = IntegrityError("Duplicate entry", None, None)
        
#         with pytest.raises(APIException) as exc_info:
#             insert_record(mock_record)
        
#         assert exc_info.value.status_code == 417
#         assert exc_info.value.error_code == ErrorCode.INTEGRITY_ERROR


# # ==================== Get Records Tests ====================

# class TestGetRecords:
#     """Test get function"""
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     @patch('storage.storage_broker.medicom_store.get_records')
#     def test_get_records_success(self, mock_get_records, mock_get_engine, mock_records, mock_engine):
#         """Test successful record retrieval"""
#         mock_get_engine.return_value = mock_engine
#         mock_get_records.return_value = mock_records
        
#         result = get(TestModel, offset=0, limit=10)
        
#         assert result == mock_records
#         assert len(result) == 3
#         mock_get_records.assert_called_once()
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     @patch('storage.storage_broker.medicom_store.get_records')
#     def test_get_records_with_conditions(self, mock_get_records, mock_get_engine, mock_records, mock_engine):
#         """Test record retrieval with conditions"""
#         mock_get_engine.return_value = mock_engine
#         mock_get_records.return_value = mock_records
#         conditions = {"id": 1}
        
#         result = get(TestModel, conditions=conditions, offset=0, limit=10)
        
#         assert result == mock_records
#         mock_get_records.assert_called_once_with(
#             mock_engine, TestModel, conditions, None, None, 0, 10
#         )
    
#     def test_get_records_limit_exceeded(self):
#         """Test record retrieval with limit exceeding maximum"""
#         with pytest.raises(APIException) as exc_info:
#             get(TestModel, limit=1001)
        
#         assert exc_info.value.status_code == 400
#         assert exc_info.value.error_code == ErrorCode.VALIDATION_ERROR
#         assert "Limit cannot exceed 1000" in exc_info.value.message
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     def test_get_records_engine_failure(self, mock_get_engine):
#         """Test record retrieval when engine fails"""
#         mock_get_engine.return_value = None
        
#         with pytest.raises(APIException) as exc_info:
#             get(TestModel, offset=0, limit=10)
        
#         assert exc_info.value.status_code == 400


# # ==================== Count Records Tests ====================

# class TestCountRecords:
#     """Test count function"""
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     @patch('storage.storage_broker.medicom_store.count_records')
#     def test_count_records_success(self, mock_count_records, mock_get_engine, mock_engine):
#         """Test successful record count"""
#         mock_get_engine.return_value = mock_engine
#         mock_count_records.return_value = 42
        
#         result = count(TestModel)
        
#         assert result == 42
#         mock_count_records.assert_called_once()
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     @patch('storage.storage_broker.medicom_store.count_records')
#     def test_count_records_with_conditions(self, mock_count_records, mock_get_engine, mock_engine):
#         """Test record count with conditions"""
#         mock_get_engine.return_value = mock_engine
#         mock_count_records.return_value = 5
#         conditions = {"status": "active"}
        
#         result = count(TestModel, conditions=conditions)
        
#         assert result == 5
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     def test_count_records_engine_failure(self, mock_get_engine):
#         """Test count when engine fails"""
#         mock_get_engine.return_value = None
        
#         with pytest.raises(APIException) as exc_info:
#             count(TestModel)
        
#         assert exc_info.value.status_code == 400


# # ==================== Delete Record Tests ====================

# class TestDeleteRecord:
#     """Test delete_record function"""
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     @patch('storage.storage_broker.medicom_store.delete_record')
#     def test_delete_record_success(self, mock_delete_record, mock_get_engine, mock_record, mock_engine):
#         """Test successful record deletion"""
#         mock_get_engine.return_value = mock_engine
#         mock_delete_record.return_value = None
        
#         result = delete_record(mock_record)
        
#         assert result is True
#         mock_delete_record.assert_called_once_with(mock_engine, mock_record)
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     @patch('storage.storage_broker.medicom_store.delete_record')
#     def test_delete_record_failure(self, mock_delete_record, mock_get_engine, mock_record, mock_engine):
#         """Test record deletion failure"""
#         mock_get_engine.return_value = mock_engine
#         mock_delete_record.side_effect = Exception("Delete failed")
        
#         with pytest.raises(APIException) as exc_info:
#             delete_record(mock_record)
        
#         assert exc_info.value.status_code == 500


# # ==================== Update Record Tests ====================

# class TestUpdateRecord:
#     """Test update_record function"""
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     @patch('storage.storage_broker.medicom_store.update_record')
#     def test_update_record_success(self, mock_update_record, mock_get_engine, mock_record, mock_engine):
#         """Test successful record update"""
#         mock_get_engine.return_value = mock_engine
#         mock_update_record.return_value = mock_record
        
#         result = update_record(mock_record)
        
#         assert result == mock_record
#         mock_update_record.assert_called_once_with(mock_engine, mock_record)
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     @patch('storage.storage_broker.medicom_store.update_record')
#     def test_update_record_failure(self, mock_update_record, mock_get_engine, mock_record, mock_engine):
#         """Test record update failure"""
#         mock_get_engine.return_value = mock_engine
#         mock_update_record.side_effect = Exception("Update failed")
        
#         with pytest.raises(APIException) as exc_info:
#             update_record(mock_record)
        
#         assert exc_info.value.status_code == 500


# # ==================== Delete Record By ID Tests ====================

# class TestDeleteRecordById:
#     """Test delete_record_by_id function"""
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     @patch('storage.storage_broker.medicom_store.delete_record_by_id')
#     def test_delete_record_by_id_success(self, mock_delete_by_id, mock_get_engine, mock_engine):
#         """Test successful record deletion by ID"""
#         mock_get_engine.return_value = mock_engine
#         mock_delete_by_id.return_value = True
        
#         result = delete_record_by_id(TestModel, 123)
        
#         assert result is True
#         mock_delete_by_id.assert_called_once_with(mock_engine, TestModel, 123)
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     @patch('storage.storage_broker.medicom_store.delete_record_by_id')
#     def test_delete_record_by_id_failure(self, mock_delete_by_id, mock_get_engine, mock_engine):
#         """Test record deletion by ID failure"""
#         mock_get_engine.return_value = mock_engine
#         mock_delete_by_id.side_effect = Exception("Delete failed")
        
#         with pytest.raises(APIException) as exc_info:
#             delete_record_by_id(TestModel, 123)
        
#         assert exc_info.value.status_code == 500


# # ==================== Search Records Tests ====================

# class TestSearchRecords:
#     """Test search_records function"""
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     @patch('storage.storage_broker.medicom_store.search_records')
#     def test_search_records_success(self, mock_search_records, mock_get_engine, mock_records, mock_engine):
#         """Test successful record search"""
#         mock_get_engine.return_value = mock_engine
#         mock_search_records.return_value = mock_records
#         search_query = "test"
#         search_fields = ["name", "description"]
        
#         result = search_records(
#             TestModel,
#             search_query=search_query,
#             search_fields=search_fields,
#             offset=0,
#             limit=20
#         )
        
#         assert result == mock_records
#         mock_search_records.assert_called_once()
    
#     def test_search_records_short_query(self):
#         """Test search with query too short"""
#         with pytest.raises(APIException) as exc_info:
#             search_records(TestModel, search_query="a", search_fields=["name"])
        
#         assert exc_info.value.status_code == 400
#         assert "at least 2 characters" in exc_info.value.message
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     @patch('storage.storage_broker.medicom_store.search_records')
#     def test_search_records_limit_capping(self, mock_search_records, mock_get_engine, mock_engine):
#         """Test search with limit exceeding maximum"""
#         mock_get_engine.return_value = mock_engine
#         mock_search_records.return_value = []
        
#         result = search_records(
#             TestModel,
#             search_query="test",
#             search_fields=["name"],
#             limit=200
#         )
        
#         assert result == []
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     def test_search_records_engine_failure(self, mock_get_engine):
#         """Test search when engine fails"""
#         mock_get_engine.return_value = None
        
#         with pytest.raises(APIException) as exc_info:
#             search_records(TestModel, search_query="test", search_fields=["name"])
        
#         assert exc_info.value.status_code == 400


# # ==================== Search By Location Tests ====================

# class TestSearchByLocation:
#     """Test search_by_filter function"""
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     @patch('storage.storage_broker.medicom_store.get_records_by_filter')
#     def test_search_by_filter_success(self, mock_get_by_filter, mock_get_engine, mock_records, mock_engine):
#         """Test successful location-based search"""
#         mock_get_engine.return_value = mock_engine
#         mock_get_by_filter.return_value = mock_records
        
#         result = search_by_filter(
#             TestModel,
#             ordering_attr="distance",
#             offset=0,
#             limit=20
#         )
        
#         assert result == mock_records
#         mock_get_by_filter.assert_called_once()
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     @patch('storage.storage_broker.medicom_store.get_records_by_filter')
#     def test_search_by_filter_limit_capping(self, mock_get_by_filter, mock_get_engine, mock_engine):
#         """Test location search with limit exceeding maximum"""
#         mock_get_engine.return_value = mock_engine
#         mock_get_by_filter.return_value = []
        
#         result = search_by_filter(TestModel, limit=200)
        
#         assert result == []
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     def test_search_by_filter_engine_failure(self, mock_get_engine):
#         """Test location search when engine fails"""
#         mock_get_engine.return_value = None
        
#         with pytest.raises(APIException) as exc_info:
#             search_by_filter(TestModel)
        
#         assert exc_info.value.status_code == 400


# # ==================== Validation Tests ====================

# class TestValidation:
#     """Test validation helper functions"""
    
#     def test_validate_table_name_success(self):
#         """Test successful table name validation"""
#         result = validate_table_name(TestModel)
#         assert result is True
    
#     def test_validate_table_name_none(self):
#         """Test table name validation with None"""
#         with pytest.raises(APIException) as exc_info:
#             validate_table_name(None)
        
#         assert exc_info.value.status_code == 400
#         assert "Table cannot be None" in exc_info.value.message
#         assert exc_info.value.error_code == ErrorCode.VALIDATION_ERROR
    
#     def test_validate_pagination_success(self):
#         """Test successful pagination validation"""
#         validate_pagination(0, 10, 100)
#         validate_pagination(50, 100, 1000)
    
#     def test_validate_pagination_negative_offset(self):
#         """Test pagination with negative offset"""
#         with pytest.raises(APIException) as exc_info:
#             validate_pagination(-1, 10)
        
#         assert exc_info.value.status_code == 400
#         assert "Offset must be non-negative" in exc_info.value.message
#         assert exc_info.value.error_code == ErrorCode.VALIDATION_ERROR
    
#     def test_validate_pagination_zero_limit(self):
#         """Test pagination with zero limit"""
#         with pytest.raises(APIException) as exc_info:
#             validate_pagination(0, 0)
        
#         assert exc_info.value.status_code == 400
#         assert "Limit must be between 1 and" in exc_info.value.message
#         assert exc_info.value.error_code == ErrorCode.VALIDATION_ERROR
    
#     def test_validate_pagination_limit_too_high(self):
#         """Test pagination with limit too high"""
#         with pytest.raises(APIException) as exc_info:
#             validate_pagination(0, 2000, 1000)
        
#         assert exc_info.value.status_code == 400
#         assert "Limit must be between 1 and 1000" in exc_info.value.message
#         assert exc_info.value.error_code == ErrorCode.VALIDATION_ERROR


# # ==================== Integration Tests ====================

# class TestIntegration:
#     """Integration-style tests with mocked dependencies"""
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     @patch('storage.storage_broker.medicom_store.add_record')
#     @patch('storage.storage_broker.medicom_store.get_records')
#     @patch('storage.storage_broker.medicom_store.update_record')
#     @patch('storage.storage_broker.medicom_store.delete_record')
#     def test_crud_workflow(
#         self, mock_delete_record, mock_update_record, 
#         mock_get_records, mock_add_record, mock_get_engine, 
#         mock_record, mock_records, mock_engine
#     ):
#         """Test complete CRUD workflow with proper mocks"""
#         mock_get_engine.return_value = mock_engine
        
#         # Create
#         mock_add_record.return_value = mock_record
#         created = insert_record(mock_record)
#         assert created == mock_record
        
#         # Read
#         mock_get_records.return_value = mock_records
#         retrieved = get(TestModel, conditions={"id": 1})
#         assert retrieved == mock_records
        
#         # Update
#         mock_update_record.return_value = mock_record
#         updated = update_record(mock_record)
#         assert updated == mock_record
        
#         # Delete
#         mock_delete_record.return_value = None
#         result = delete_record(mock_record)
#         assert result is True
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     @patch('storage.storage_broker.medicom_store.search_records')
#     def test_search_workflow(self, mock_search, mock_get_engine, mock_records, mock_engine):
#         """Test search workflow"""
#         mock_get_engine.return_value = mock_engine
#         mock_search.return_value = mock_records
        
#         results = search_records(
#             TestModel,
#             search_query="test query",
#             search_fields=["name", "description"],
#             offset=0,
#             limit=20
#         )
        
#         assert len(results) == 3
#         mock_search.assert_called_once()


# # ==================== Performance Tests ====================

# class TestPerformance:
#     """Basic performance tests"""
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     @patch('storage.storage_broker.medicom_store.get_records')
#     def test_get_records_performance(self, mock_get_records, mock_get_engine, mock_records, mock_engine):
#         """Test get_records performance"""
#         import time
        
#         mock_get_engine.return_value = mock_engine
#         mock_get_records.return_value = mock_records
        
#         start_time = time.time()
#         get(TestModel, offset=0, limit=100)
#         end_time = time.time()
        
#         assert (end_time - start_time) < 0.5
    
#     @patch('storage.storage_broker.get_engine_with_retry')
#     @patch('storage.storage_broker.medicom_store.search_records')
#     def test_search_performance(self, mock_search, mock_get_engine, mock_records, mock_engine):
#         """Test search performance"""
#         import time
        
#         mock_get_engine.return_value = mock_engine
#         mock_search.return_value = mock_records
        
#         start_time = time.time()
#         search_records(TestModel, search_query="test", search_fields=["name"], limit=50)
#         end_time = time.time()
        
#         assert (end_time - start_time) < 0.5


# # ==================== Run Tests ====================

# if __name__ == "__main__":
#     pytest.main([__file__, "-v", "--tb=short"])