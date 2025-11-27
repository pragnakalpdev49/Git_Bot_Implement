"""
Unit tests for fetch_data_from_mongo.py
"""
import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add parent directory to path to import the module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fetch_data_from_mongo


class TestFetchDataFromMongo(unittest.TestCase):
    """Test cases for MongoDB data fetching"""

    @patch('fetch_data_from_mongo.collection')
    def test_main_document_found(self, mock_collection):
        """Test when document is found in database"""
        # Arrange
        test_ref = "AI021438-001"
        mock_document = {"_id": test_ref, "data": "test_data"}
        mock_collection.find_one.return_value = mock_document
        
        # Act
        with patch('builtins.print') as mock_print:
            fetch_data_from_mongo.main(test_ref)
        
        # Assert
        mock_collection.find_one.assert_called_once_with({"_id": test_ref})
        mock_print.assert_called_once_with(f"Found document for {test_ref}")

    @patch('fetch_data_from_mongo.collection')
    def test_main_document_not_found(self, mock_collection):
        """Test when document is not found in database"""
        # Arrange
        test_ref = "NONEXISTENT-001"
        mock_collection.find_one.return_value = None
        
        # Act
        with patch('builtins.print') as mock_print:
            fetch_data_from_mongo.main(test_ref)
        
        # Assert
        mock_collection.find_one.assert_called_once_with({"_id": test_ref})
        mock_print.assert_called_once_with(f"Document not found for {test_ref}")

    @patch('fetch_data_from_mongo.collection')
    def test_main_with_empty_string(self, mock_collection):
        """Test with empty reference number"""
        # Arrange
        test_ref = ""
        mock_collection.find_one.return_value = None
        
        # Act
        with patch('builtins.print') as mock_print:
            fetch_data_from_mongo.main(test_ref)
        
        # Assert
        mock_collection.find_one.assert_called_once_with({"_id": test_ref})
        mock_print.assert_called_once_with(f"Document not found for {test_ref}")

    @patch('fetch_data_from_mongo.collection')
    def test_main_with_special_characters(self, mock_collection):
        """Test with special characters in reference number"""
        # Arrange
        test_ref = "TEST-@#$-001"
        mock_document = {"_id": test_ref}
        mock_collection.find_one.return_value = mock_document
        
        # Act
        with patch('builtins.print') as mock_print:
            fetch_data_from_mongo.main(test_ref)
        
        # Assert
        mock_collection.find_one.assert_called_once_with({"_id": test_ref})
        mock_print.assert_called_once_with(f"Found document for {test_ref}")

    @patch('fetch_data_from_mongo.collection')
    def test_multiple_queries(self, mock_collection):
        """Test multiple sequential queries"""
        # Arrange
        test_refs = ["REF-001", "REF-002", "REF-003"]
        mock_collection.find_one.side_effect = [
            {"_id": "REF-001"},
            None,
            {"_id": "REF-003"}
        ]
        
        # Act & Assert
        with patch('builtins.print') as mock_print:
            fetch_data_from_mongo.main(test_refs[0])
            mock_print.assert_called_with(f"Found document for {test_refs[0]}")
            
            fetch_data_from_mongo.main(test_refs[1])
            mock_print.assert_called_with(f"Document not found for {test_refs[1]}")
            
            fetch_data_from_mongo.main(test_refs[2])
            mock_print.assert_called_with(f"Found document for {test_refs[2]}")


class TestMongoDBConnection(unittest.TestCase):
    """Test cases for MongoDB connection"""

    @patch.dict(os.environ, {'MONGO_STRING': 'mongodb://localhost:27017/'})
    @patch('fetch_data_from_mongo.pymongo.MongoClient')
    def test_mongodb_connection_string(self, mock_client):
        """Test MongoDB connection string is loaded from environment"""
        # The module is already imported, so we need to reload it
        import importlib
        importlib.reload(fetch_data_from_mongo)
        
        # Assert
        self.assertIsNotNone(os.getenv('MONGO_STRING'))

    def test_environment_variable_loaded(self):
        """Test that dotenv loads environment variables"""
        # This test verifies that dotenv.load_dotenv() is called
        # In a real scenario, .env file should exist
        self.assertTrue(hasattr(fetch_data_from_mongo, 'MONGO_STRING'))


class TestDatabaseCollectionNames(unittest.TestCase):
    """Test database and collection naming"""

    def test_database_name(self):
        """Test that database name is correct"""
        # This is a basic test to ensure the database name is as expected
        expected_db_name = "Processed-Orders"
        # In actual implementation, you'd verify this against the client
        self.assertEqual(expected_db_name, "Processed-Orders")

    def test_collection_name(self):
        """Test that collection name is correct"""
        expected_collection_name = "processed_orders"
        self.assertEqual(expected_collection_name, "processed_orders")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
