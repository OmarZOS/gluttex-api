# tests/test_product_service.py
import pytest
import asyncio
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import BackgroundTasks
from core.api_models import Product_API, ProductImage_API, Iproduct_API
from core.exceptions.handler import APIException
from core.models import Product, ProductImage, Iproduct
from services.product_service import ProductService, subscribers


class TestProductService:
    
    @pytest.fixture
    def product_service(self):
        """Create ProductService with mocked dependencies"""
        service = ProductService()
        service.product_repo = MagicMock()
        service.iproduct_repo = MagicMock()
        service.ai_service = AsyncMock()
        return service
    
    @pytest.fixture
    def sample_product_api(self):
        """Sample Product_API data"""
        return Product_API(
            id_product=1,
            product_provider_id=10,
            id_product_category=5,
            product_category_id=5,
            product_price=19.99,
            product_quantity=100,
            product_name="Test Product",
            product_brand="Test Brand",
            product_barcode="123456789",
            product_description="Test description",
            product_quantifier="piece",
            product_owner=100
        )
    
    @pytest.fixture
    def sample_product_model(self, sample_product_api):
        """Sample Product model with SQLAlchemy-like behavior"""
        product = MagicMock(spec=Product)
        product.id_product = 1
        product.product_name = "Test Product"
        product.product_brand = "Test Brand"
        product.product_barcode = "123456789"
        product.product_price = 19.99
        product.product_quantity = 100
        product.product_quantifier = "piece"
        product.product_description = "Test description"
        product.product_owner = 100
        product.product_category_id = 5
        product.product_image = []
        product.product_origin = None
        # Add _sa_instance_state to avoid SQLAlchemy attribute errors
        product._sa_instance_state = MagicMock()
        return product
    
    @pytest.fixture
    def sample_iproduct_api(self):
        """Sample Iproduct_API data"""
        return Iproduct_API(
            id_iproduct=0,
            iproduct_name="AI Recognized Product",
            iproduct_barcode="987654321",
            iproduct_brand="AI Brand",
            iproduct_estimated_price=29.99,
            iproduct_price_currency="USD",
            iproduct_gluten_status="gluten_free",
            iproduct_info_source="openai",
            iproduct_info_confidence=0.95,
            iproduct_model_name="gpt-4",
            iproduct_image_url="http://example.com/product.jpg"
        )
    
    @pytest.fixture
    def sample_image_api(self):
        """Sample ProductImage_API data"""
        return ProductImage_API(
            id_product_image=0,
            product_image_url="http://example.com/image.jpg",
            product_ref_id=1
        )
    
    # ========== GET Methods Tests ==========
    
    def test_get_product_by_id_found(self, product_service, sample_product_model):
        """Test getting product by ID when found"""
        product_service.product_repo.get_product_by_id.return_value = sample_product_model
        
        result = product_service.get_product_by_id(1)
        
        assert result == sample_product_model
        product_service.product_repo.get_product_by_id.assert_called_once_with(1, eager_load=False)
    
    def test_get_product_by_id_with_eager_load(self, product_service, sample_product_model):
        """Test getting product by ID with eager loading"""
        product_service.product_repo.get_product_by_id.return_value = sample_product_model
        
        result = product_service.get_product_by_id(1, full=True)
        
        product_service.product_repo.get_product_by_id.assert_called_once_with(1, eager_load=True)
    
    def test_get_product_by_id_not_found(self, product_service):
        """Test getting product by ID when not found"""
        product_service.product_repo.get_product_by_id.return_value = None
        
        with pytest.raises(APIException) as exc_info:
            product_service.get_product_by_id(999)
        
        assert exc_info.value.status == 404
    
    def test_get_all_products(self, product_service):
        """Test getting all products with filters"""
        expected_products = [MagicMock(), MagicMock()]
        product_service.product_repo.get_all_products.return_value = expected_products
        
        result = product_service.get_all_products(
            user_id=100, provider_id=10, category_id=5, offset=0, limit=20
        )
        
        assert result == expected_products
        product_service.product_repo.get_all_products.assert_called_once_with(100, 10, 5, 0, 20)
    
    def test_get_all_products_default_params(self, product_service):
        """Test getting all products with default parameters"""
        expected_products = []
        product_service.product_repo.get_all_products.return_value = expected_products
        
        result = product_service.get_all_products()
        
        product_service.product_repo.get_all_products.assert_called_once_with(0, 0, 0, 0, 10)
    
    def test_get_products_by_category(self, product_service):
        """Test getting products by category"""
        expected_products = [MagicMock(), MagicMock(), MagicMock()]
        product_service.product_repo.get_products_by_category.return_value = expected_products
        
        result = product_service.get_products_by_category(5, offset=10, limit=50)
        
        assert result == expected_products
        product_service.product_repo.get_products_by_category.assert_called_once_with(5, 10, 50)
    
    def test_get_product_categories(self, product_service):
        """Test getting all product categories"""
        expected_categories = [MagicMock(), MagicMock()]
        product_service.product_repo.get_product_categories.return_value = expected_categories
        
        result = product_service.get_product_categories()
        
        assert result == expected_categories
    
    # ========== Create Product Tests ==========
    
    @pytest.mark.asyncio
    async def test_create_product_success(self, product_service, sample_product_api):
        """Test creating a product successfully"""
        product_service.product_repo.get_product_by_id.return_value = None
        
        mock_category = MagicMock()
        mock_category.id_product_category = 5
        product_service.product_repo.get_product_category_by_id.return_value = mock_category
        
        expected_product = MagicMock()
        product_service.product_repo.create_product.return_value = expected_product
        
        result = await product_service.create_product(sample_product_api)
        
        assert result == expected_product
        product_service.product_repo.create_product.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_product_with_image(self, product_service, sample_product_api, sample_image_api):
        """Test creating a product with an image"""
        product_service.product_repo.get_product_by_id.return_value = None
        
        mock_category = MagicMock()
        mock_category.id_product_category = 5
        product_service.product_repo.get_product_category_by_id.return_value = mock_category
        
        expected_product = MagicMock()
        product_service.product_repo.create_product.return_value = expected_product
        
        result = await product_service.create_product(sample_product_api, image=sample_image_api)
        
        assert result == expected_product
        call_args = product_service.product_repo.create_product.call_args[0][0]
        assert len(call_args.product_image) == 1
        assert call_args.product_image[0].product_image_url == "http://example.com/image.jpg"
    
    @pytest.mark.asyncio
    async def test_create_product_with_iproduct_new(self, product_service, sample_product_api, sample_iproduct_api):
        """Test creating a product with new IProduct data"""
        product_service.product_repo.get_product_by_id.return_value = None
        
        mock_category = MagicMock()
        mock_category.id_product_category = 5
        product_service.product_repo.get_product_category_by_id.return_value = mock_category
        
        product_service.iproduct_repo.get_by_id.return_value = None
        
        expected_product = MagicMock()
        product_service.product_repo.create_product.return_value = expected_product
        
        result = await product_service.create_product(sample_product_api, iproduct=sample_iproduct_api)
        
        assert result == expected_product
        call_args = product_service.product_repo.create_product.call_args[0][0]
        assert call_args.product_origin is not None
    
    @pytest.mark.asyncio
    async def test_create_product_already_exists(self, product_service, sample_product_api):
        """Test creating a product that already exists"""
        product_service.product_repo.get_product_by_id.return_value = MagicMock()
        
        with pytest.raises(APIException) as exc_info:
            await product_service.create_product(sample_product_api)
        
        assert exc_info.value.status == 409
    
    @pytest.mark.asyncio
    async def test_create_product_invalid_category(self, product_service, sample_product_api):
        """Test creating a product with invalid category"""
        product_service.product_repo.get_product_by_id.return_value = None
        product_service.product_repo.get_product_category_by_id.return_value = None
        
        with pytest.raises(APIException) as exc_info:
            await product_service.create_product(sample_product_api)
        
        assert exc_info.value.status == 404
    
    @pytest.mark.asyncio
    async def test_create_product_db_error(self, product_service, sample_product_api):
        """Test creating a product when database error occurs"""
        product_service.product_repo.get_product_by_id.return_value = None
        
        mock_category = MagicMock()
        mock_category.id_product_category = 5
        product_service.product_repo.get_product_category_by_id.return_value = mock_category
        
        product_service.product_repo.create_product.side_effect = Exception("Database error")
        
        with pytest.raises(APIException) as exc_info:
            await product_service.create_product(sample_product_api)
        
        assert exc_info.value.status == 417
    
    # ========== Update Product Tests ==========
    
    def test_update_product_success(self, product_service, sample_product_api, sample_product_model):
        """Test updating a product successfully"""
        mock_category = MagicMock()
        mock_category.id_product_category = 5
        product_service.product_repo.get_product_category_by_id.return_value = mock_category
        
        product_service.product_repo.get_product_by_id.return_value = sample_product_model
        product_service.product_repo.update_product.return_value = sample_product_model
        
        result = product_service.update_product(1, sample_product_api)
        
        assert result == sample_product_model
        assert sample_product_model.product_name == sample_product_api.product_name
        assert sample_product_model.product_price == sample_product_api.product_price
    
    def test_update_product_invalid_category(self, product_service, sample_product_api):
        """Test updating a product with invalid category"""
        product_service.product_repo.get_product_category_by_id.return_value = None
        
        with pytest.raises(APIException) as exc_info:
            product_service.update_product(1, sample_product_api)
        
        assert exc_info.value.status == 404
    
    def test_update_product_not_found(self, product_service, sample_product_api):
        """Test updating a product that doesn't exist"""
        mock_category = MagicMock()
        mock_category.id_product_category = 5
        product_service.product_repo.get_product_category_by_id.return_value = mock_category
        product_service.product_repo.get_product_by_id.return_value = None
        
        with pytest.raises(APIException) as exc_info:
            product_service.update_product(999, sample_product_api)
        
        assert exc_info.value.status == 404
    
    def test_update_product_with_image_new(self, product_service, sample_product_api, sample_product_model, sample_image_api):
        """Test updating a product with a new image"""
        mock_category = MagicMock()
        mock_category.id_product_category = 5
        product_service.product_repo.get_product_category_by_id.return_value = mock_category
        
        product_service.product_repo.get_product_by_id.return_value = sample_product_model
        product_service.product_repo.update_product.return_value = sample_product_model
        product_service.product_repo.get_product_image_by_id.return_value = []
        
        result = product_service.update_product(1, sample_product_api, image=sample_image_api)
        
        assert result == sample_product_model
        product_service.product_repo.create_product_image.assert_called_once()
    
    def test_update_product_with_existing_image(self, product_service, sample_product_api, sample_product_model):
        """Test updating a product with an existing image"""
        sample_image_api = ProductImage_API(
            id_product_image=10,
            product_image_url="http://example.com/updated.jpg",
            product_ref_id=1
        )
        
        mock_category = MagicMock()
        mock_category.id_product_category = 5
        product_service.product_repo.get_product_category_by_id.return_value = mock_category
        
        product_service.product_repo.get_product_by_id.return_value = sample_product_model
        
        mock_existing_image = [MagicMock()]
        product_service.product_repo.get_product_image_by_id.return_value = mock_existing_image
        product_service.product_repo.update_product.return_value = sample_product_model
        
        result = product_service.update_product(1, sample_product_api, image=sample_image_api)
        
        assert result == sample_product_model
        product_service.product_repo.update_product_image.assert_called_once()
    
    def test_update_product_with_background_notification(self, product_service, sample_product_api, sample_product_model):
        """Test updating a product with background notification"""
        mock_category = MagicMock()
        mock_category.id_product_category = 5
        product_service.product_repo.get_product_category_by_id.return_value = mock_category
        
        product_service.product_repo.get_product_by_id.return_value = sample_product_model
        product_service.product_repo.update_product.return_value = sample_product_model
        
        background_tasks = MagicMock(spec=BackgroundTasks)
        
        result = product_service.update_product(1, sample_product_api, background_tasks=background_tasks)
        
        assert result == sample_product_model
        background_tasks.add_task.assert_called_once()
    
    def test_update_product_db_error(self, product_service, sample_product_api, sample_product_model):
        """Test updating a product when database error occurs"""
        mock_category = MagicMock()
        mock_category.id_product_category = 5
        product_service.product_repo.get_product_category_by_id.return_value = mock_category
        
        product_service.product_repo.get_product_by_id.return_value = sample_product_model
        product_service.product_repo.update_product.side_effect = Exception("Database error")
        
        with pytest.raises(APIException) as exc_info:
            product_service.update_product(1, sample_product_api)
        
        assert exc_info.value.status == 417
    
    # ========== Delete Product Tests ==========
    
    def test_delete_product_success(self, product_service, sample_product_model):
        """Test deleting a product successfully"""
        product_service.product_repo.get_product_by_id.return_value = sample_product_model
        product_service.product_repo.delete_product.return_value = True
        
        result = product_service.delete_product(1)
        
        assert result is True
        product_service.product_repo.delete_product.assert_called_once_with(sample_product_model)
    
    def test_delete_product_not_found(self, product_service):
        """Test deleting a product that doesn't exist"""
        product_service.product_repo.get_product_by_id.return_value = None
        
        with pytest.raises(APIException) as exc_info:
            product_service.delete_product(999)
        
        assert exc_info.value.status == 404
    
    # ========== IProduct Methods Tests ==========
    
    def test_get_iproduct_by_barcode(self, product_service):
        """Test getting IProduct by barcode"""
        expected_iproducts = [MagicMock(), MagicMock()]
        product_service.iproduct_repo.get_by_barcode.return_value = expected_iproducts
        
        result = product_service.get_iproduct_by_barcode("123456789")
        
        assert result == expected_iproducts
        product_service.iproduct_repo.get_by_barcode.assert_called_once_with("123456789")
    
    def test_get_iproduct_by_id(self, product_service):
        """Test getting IProduct by ID"""
        expected_iproduct = MagicMock()
        product_service.iproduct_repo.get_by_id.return_value = expected_iproduct
        
        result = product_service.get_iproduct_by_id(1)
        
        assert result == expected_iproduct
        product_service.iproduct_repo.get_by_id.assert_called_once_with(1)
    
    # ========== AI Service Methods Tests ==========
    
    @pytest.mark.asyncio
    async def test_recognize_product_from_image(self, product_service):
        """Test product recognition from image"""
        mock_ai_result = {"name": "Test Product", "brand": "Test Brand"}
        mock_model_name = "gpt-4"
        
        # Create an async function for the mock
        async def mock_recognize(image_bytes, language):
            return mock_ai_result, mock_model_name
        
        product_service.ai_service.recognize_product_from_image = mock_recognize
        
        mock_iproduct = MagicMock()
        product_service.ai_service.format_ai_result_to_iproduct = MagicMock(return_value=mock_iproduct)
        
        image_bytes = b"fake_image_data"
        result = await product_service.recognize_product_from_image(image_bytes, "en")
        
        assert result == mock_iproduct
        product_service.ai_service.format_ai_result_to_iproduct.assert_called_once_with(mock_ai_result, mock_model_name)
    
    @pytest.mark.asyncio
    async def test_get_product_info_by_barcode(self, product_service):
        """Test getting product info by barcode"""
        mock_ai_result = {"name": "Product", "barcode": "123"}
        mock_model_name = "gpt-4"
        
        async def mock_generate(barcode, language):
            return mock_ai_result, mock_model_name
        
        product_service.ai_service.generate_product_info_by_barcode = mock_generate
        
        mock_iproduct = MagicMock()
        product_service.ai_service.format_ai_result_to_iproduct = MagicMock(return_value=mock_iproduct)
        
        result = await product_service.get_product_info_by_barcode("123456789", "fr")
        
        assert result == mock_iproduct
    
    # ========== Helper Method Tests ==========
    
    def test_build_product_model(self, product_service, sample_product_api):
        """Test building Product model from API data"""
        result = product_service._build_product_model(sample_product_api)
        
        assert result.product_name == sample_product_api.product_name
        assert result.product_brand == sample_product_api.product_brand
        assert result.product_barcode == sample_product_api.product_barcode
        assert result.product_price == sample_product_api.product_price
        assert result.product_quantifier == sample_product_api.product_quantifier
        assert result.product_quantity == sample_product_api.product_quantity
        assert result.product_description == sample_product_api.product_description
        assert result.product_owner == sample_product_api.product_owner
        assert result.created is not None
        assert result.last_updated is not None
    
    def test_create_iproduct_from_api(self, product_service, sample_iproduct_api):
        """Test creating Iproduct from API data"""
        result = product_service._create_iproduct_from_api(sample_iproduct_api)
        
        assert result.iproduct_name == "AI Recognized Product"
        assert result.iproduct_barcode == "987654321"
        assert result.iproduct_brand == "AI Brand"
        assert result.iproduct_estimated_price == 29.99
        assert result.iproduct_price_currency == "USD"
        assert result.iproduct_gluten_status == "gluten_free"
        assert result.iproduct_info_source == "openai"
        assert result.iproduct_info_confidence == 0.95
    
    def test_create_iproduct_from_api_defaults(self, product_service):
        """Test creating Iproduct from API with missing values"""
        empty_api = Iproduct_API(
            id_iproduct=0,
            iproduct_name=None,
            iproduct_barcode="123",
            iproduct_brand=None,
            iproduct_estimated_price=None,
            iproduct_price_currency=None,
            iproduct_gluten_status=None,
            iproduct_info_source=None,
            iproduct_info_confidence=None,
            iproduct_model_name=None,
            iproduct_image_url=None
        )
        
        result = product_service._create_iproduct_from_api(empty_api)
        
        assert result.iproduct_name == "Unknown"
        assert result.iproduct_brand == "Unknown"
        assert result.iproduct_estimated_price == 0.0
        assert result.iproduct_price_currency == "DZD"
        assert result.iproduct_gluten_status == "unknown"
        assert result.iproduct_info_source == "ai_analysis"
        assert result.iproduct_info_confidence == 0.0
    
    def test_update_iproduct(self, product_service):
        """Test updating existing Iproduct"""
        existing = MagicMock()
        existing.iproduct_name = "Old Name"
        existing.iproduct_brand = "Old Brand"
        existing.iproduct_estimated_price = 10.0
        
        new_data = Iproduct_API(
            id_iproduct=1,
            iproduct_name="New Name",
            iproduct_brand="New Brand",
            iproduct_estimated_price=20.0,
            iproduct_gluten_status="contains_gluten",
            iproduct_info_source="manual",
            iproduct_info_confidence=0.8
        )
        
        product_service._update_iproduct(existing, new_data)
        
        assert existing.iproduct_name == "New Name"
        assert existing.iproduct_brand == "New Brand"
        assert existing.iproduct_estimated_price == 20.0
        assert existing.iproduct_gluten_status == "contains_gluten"
        assert existing.iproduct_info_source == "manual"
        assert existing.iproduct_info_confidence == 0.8
        product_service.iproduct_repo.update.assert_called_once_with(existing)
    
    def test_handle_product_image_new(self, product_service, sample_product_model, sample_image_api):
        """Test handling new product image creation"""
        product_service.product_repo.create_product_image.return_value = MagicMock()
        
        product_service._handle_product_image(sample_image_api, sample_product_model)
        
        product_service.product_repo.create_product_image.assert_called_once()
        call_arg = product_service.product_repo.create_product_image.call_args[0][0]
        assert call_arg.product_image_url == "http://example.com/image.jpg"
        assert call_arg.product_ref == sample_product_model
    
    def test_handle_product_image_update(self, product_service, sample_product_model):
        """Test handling existing product image update"""
        sample_image_api = ProductImage_API(
            id_product_image=10,
            product_image_url="http://example.com/updated.jpg",
            product_ref_id=1
        )
        
        mock_existing_image = MagicMock()
        product_service.product_repo.get_product_image_by_id.return_value = [mock_existing_image]
        product_service.product_repo.update_product_image.return_value = mock_existing_image
        
        product_service._handle_product_image(sample_image_api, sample_product_model)
        
        assert mock_existing_image.product_image_url == "http://example.com/updated.jpg"
        product_service.product_repo.update_product_image.assert_called_once_with(mock_existing_image)
    
    def test_handle_product_image_create_failure(self, product_service, sample_product_model, sample_image_api):
        """Test handling product image creation when database fails"""
        product_service.product_repo.create_product_image.side_effect = Exception("Database error")
        
        with pytest.raises(APIException) as exc_info:
            product_service._handle_product_image(sample_image_api, sample_product_model)
        
        assert exc_info.value.status == 403
    
    def test_product_to_dict(self, product_service, sample_product_model):
        """Test converting product to dictionary"""
        sample_product_model.id_product = 1
        sample_product_model.product_name = "Test"
        sample_product_model.created = datetime(2024, 1, 1, 12, 0, 0)
        sample_product_model._private_attr = "should be ignored"
        
        # Mock __dict__ to return a dictionary
        sample_product_model.__dict__ = {
            "id_product": 1,
            "product_name": "Test",
            "created": datetime(2024, 1, 1, 12, 0, 0),
            "_private_attr": "should be ignored",
            "_sa_instance_state": MagicMock()
        }
        
        result = product_service._product_to_dict(sample_product_model)
        
        assert result["id_product"] == 1
        assert result["product_name"] == "Test"
        assert result["created"] == "2024-01-01T12:00:00"
        assert "_private_attr" not in result
    
    # ========== SSE Subscriber Tests ==========
    
    @pytest.mark.asyncio
    async def test_notify_product_subscribers_success(self, product_service):
        """Test notifying product subscribers successfully"""
        global subscribers
        subscribers.clear()
        
        mock_queue = MagicMock()
        mock_queue.put_nowait = MagicMock()
        
        product_service.add_subscriber(1, mock_queue)
        
        test_data = {"id": 1, "name": "Updated Product"}
        
        await product_service._notify_product_subscribers(1, test_data)
        
        mock_queue.put_nowait.assert_called_once_with(test_data)
        
        subscribers.clear()
    
    @pytest.mark.asyncio
    async def test_notify_product_subscribers_queue_full(self, product_service):
        """Test notifying subscribers when queue is full"""
        global subscribers
        subscribers.clear()
        
        mock_queue = MagicMock()
        mock_queue.put_nowait.side_effect = asyncio.QueueFull()
        
        product_service.add_subscriber(1, mock_queue)
        
        await product_service._notify_product_subscribers(1, {"test": "data"})
        
        # Subscriber should be removed
        assert 1 not in subscribers or mock_queue not in subscribers.get(1, [])
        
        subscribers.clear()
    
    @pytest.mark.asyncio
    async def test_notify_product_subscribers_no_subscribers(self, product_service):
        """Test notifying when no subscribers exist"""
        global subscribers
        subscribers.clear()
        
        # Should not raise any exception
        await product_service._notify_product_subscribers(999, {"test": "data"})
    
    def test_add_subscriber(self, product_service):
        """Test adding a subscriber"""
        global subscribers
        subscribers.clear()
        
        mock_queue = MagicMock()
        product_service.add_subscriber(1, mock_queue)
        
        assert 1 in subscribers
        assert mock_queue in subscribers[1]
        
        subscribers.clear()
    
    def test_add_multiple_subscribers_same_product(self, product_service):
        """Test adding multiple subscribers for same product"""
        global subscribers
        subscribers.clear()
        
        queue1 = MagicMock()
        queue2 = MagicMock()
        
        product_service.add_subscriber(1, queue1)
        product_service.add_subscriber(1, queue2)
        
        assert len(subscribers[1]) == 2
        assert queue1 in subscribers[1]
        assert queue2 in subscribers[1]
        
        subscribers.clear()
    
    def test_remove_subscriber(self, product_service):
        """Test removing a subscriber"""
        global subscribers
        subscribers.clear()
        
        queue1 = MagicMock()
        queue2 = MagicMock()
        
        product_service.add_subscriber(1, queue1)
        product_service.add_subscriber(1, queue2)
        
        product_service.remove_subscriber(1, queue1)
        
        assert queue1 not in subscribers[1]
        assert queue2 in subscribers[1]
        
        subscribers.clear()
    
    def test_remove_last_subscriber(self, product_service):
        """Test removing the last subscriber for a product"""
        global subscribers
        subscribers.clear()
        
        mock_queue = MagicMock()
        product_service.add_subscriber(1, mock_queue)
        
        product_service.remove_subscriber(1, mock_queue)
        
        assert 1 not in subscribers
        
        subscribers.clear()
    
    def test_remove_nonexistent_subscriber(self, product_service):
        """Test removing a subscriber that doesn't exist"""
        global subscribers
        subscribers.clear()
        
        mock_queue = MagicMock()
        # Should not raise any exception
        product_service.remove_subscriber(1, mock_queue)
        
        subscribers.clear()
    
    # ========== Async IProduct Handling Tests ==========
    
    @pytest.mark.asyncio
    async def test_handle_iproduct_data_new(self, product_service, sample_product_model, sample_iproduct_api):
        """Test handling new IProduct data"""
        sample_iproduct_api.id_iproduct = 0
        product_service.iproduct_repo.get_by_id.return_value = None
        
        await product_service._handle_iproduct_data(sample_product_model, sample_iproduct_api)
        
        assert sample_product_model.product_origin is not None
    
    @pytest.mark.asyncio
    async def test_handle_iproduct_data_existing(self, product_service, sample_product_model, sample_iproduct_api):
        """Test handling existing IProduct data"""
        sample_iproduct_api.id_iproduct = 5
        mock_existing_iproduct = MagicMock()
        product_service.iproduct_repo.get_by_id.return_value = mock_existing_iproduct
        
        await product_service._handle_iproduct_data(sample_product_model, sample_iproduct_api)
        
        assert sample_product_model.product_origin == mock_existing_iproduct
        product_service.iproduct_repo.update.assert_called_once_with(mock_existing_iproduct)


# Run with: pytest tests/test_product_service.py -v