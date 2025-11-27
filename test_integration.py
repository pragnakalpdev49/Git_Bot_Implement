"""
Integration tests for fetch_data_from_mongo.py
These tests require a running MongoDB instance
"""
import unittest
import pymongo
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fetch_data_from_mongo


class TestMongoDBIntegration(unittest.TestCase):
    """Integration tests with actual MongoDB connection"""

    @classmethod
    def setUpClass(cls):
        """Set up test database connection"""
        # Use test MongoDB connection
        mongo_string = os.getenv("MONGO_STRING", "mongodb://localhost:27017/")
        cls.client = pymongo.MongoClient(mongo_string)
        cls.database = cls.client["Test-Processed-Orders"]
        cls.collection = cls.database["test_processed_orders"]
        
        # Insert test data
        cls.test_documents = [
            {"_id": "TEST-001", "status": "processed", "amount": 100},
            {"_id": "TEST-002", "status": "pending", "amount": 200},
            {"_id": "TEST-003", "status": "completed", "amount": 300},
        ]
        
        # Clear any existing test data
        cls.collection.delete_many({})
        
        # Insert test documents
        cls.collection.insert_many(cls.test_documents)

    @classmethod
    def tearDownClass(cls):
        """Clean up test database"""
        # Remove test data
        cls.collection.delete_many({})
        # Drop test database
        cls.client.drop_database("Test-Processed-Orders")
        cls.client.close()

    def test_find_existing_document(self):
        """Test finding an existing document"""
        result = self.collection.find_one({"_id": "TEST-001"})
        self.assertIsNotNone(result)
        self.assertEqual(result["_id"], "TEST-001")
        self.assertEqual(result["status"], "processed")

    def test_find_nonexistent_document(self):
        """Test finding a non-existent document"""
        result = self.collection.find_one({"_id": "NONEXISTENT"})
        self.assertIsNone(result)

    def test_database_connection(self):
        """Test that database connection is successful"""
        # Test connection by listing databases
        db_list = self.client.list_database_names()
        self.assertIsInstance(db_list, list)
        self.assertIn("Test-Processed-Orders", db_list)

    def test_collection_exists(self):
        """Test that collection exists in database"""
        collections = self.database.list_collection_names()
        self.assertIn("test_processed_orders", collections)

    def test_document_count(self):
        """Test document count in collection"""
        count = self.collection.count_documents({})
        self.assertEqual(count, 3)

    def test_query_by_status(self):
        """Test querying documents by status"""
        result = self.collection.find_one({"status": "completed"})
        self.assertIsNotNone(result)
        self.assertEqual(result["_id"], "TEST-003")

    def test_insert_and_retrieve(self):
        """Test inserting a new document and retrieving it"""
        new_doc = {"_id": "TEST-004", "status": "new", "amount": 400}
        self.collection.insert_one(new_doc)
        
        retrieved = self.collection.find_one({"_id": "TEST-004"})
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["amount"], 400)
        
        # Cleanup
        self.collection.delete_one({"_id": "TEST-004"})

    def test_update_document(self):
        """Test updating a document"""
        self.collection.update_one(
            {"_id": "TEST-001"},
            {"$set": {"status": "updated"}}
        )
        
        updated = self.collection.find_one({"_id": "TEST-001"})
        self.assertEqual(updated["status"], "updated")
        
        # Restore original value
        self.collection.update_one(
            {"_id": "TEST-001"},
            {"$set": {"status": "processed"}}
        )


class TestMongoDBPerformance(unittest.TestCase):
    """Performance tests for MongoDB operations"""

    @classmethod
    def setUpClass(cls):
        """Set up test database connection"""
        mongo_string = os.getenv("MONGO_STRING", "mongodb://localhost:27017/")
        cls.client = pymongo.MongoClient(mongo_string)
        cls.database = cls.client["Test-Performance"]
        cls.collection = cls.database["test_performance"]
        cls.collection.delete_many({})

    @classmethod
    def tearDownClass(cls):
        """Clean up"""
        cls.collection.delete_many({})
        cls.client.drop_database("Test-Performance")
        cls.client.close()

    def test_bulk_insert_performance(self):
        """Test bulk insert performance"""
        import time
        
        # Create 100 test documents
        docs = [{"_id": f"PERF-{i:04d}", "value": i} for i in range(100)]
        
        start_time = time.time()
        self.collection.insert_many(docs)
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Assert that bulk insert completes in reasonable time (< 1 second)
        self.assertLess(duration, 1.0)
        
        # Verify count
        count = self.collection.count_documents({})
        self.assertEqual(count, 100)
        
        # Cleanup
        self.collection.delete_many({})

    def test_query_performance(self):
        """Test query performance"""
        import time
        
        # Insert test data
        docs = [{"_id": f"QUERY-{i:04d}", "value": i} for i in range(50)]
        self.collection.insert_many(docs)
        
        start_time = time.time()
        result = self.collection.find_one({"_id": "QUERY-0025"})
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Assert query completes quickly (< 0.1 seconds)
        self.assertLess(duration, 0.1)
        self.assertIsNotNone(result)
        
        # Cleanup
        self.collection.delete_many({})


if __name__ == '__main__':
    # Check if MongoDB is available
    try:
        mongo_string = os.getenv("MONGO_STRING", "mongodb://localhost:27017/")
        client = pymongo.MongoClient(mongo_string, serverSelectionTimeoutMS=2000)
        client.server_info()
        client.close()
        
        # Run tests
        unittest.main(verbosity=2)
    except Exception as e:
        print(f"❌ MongoDB is not available: {e}")
        print("⚠️  Integration tests require a running MongoDB instance")
        print("💡 Start MongoDB or set MONGO_STRING environment variable")
        sys.exit(1)
