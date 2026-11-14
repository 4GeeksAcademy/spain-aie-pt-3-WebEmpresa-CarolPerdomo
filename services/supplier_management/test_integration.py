#!/usr/bin/env python3
"""
Integration test for Supplier Management System
Tests all endpoints and validates data flow
"""
import json
import sys
from datetime import datetime
from db import get_db, seed_suppliers, clear_db, create_supplier
from models import SupplierCreate, SupplierStatus, ProductCategory

def test_models():
    """Test Pydantic models"""
    print("\n✓ Testing Models...")
    
    # Valid supplier
    supplier = SupplierCreate(
        name="Test Supplier",
        country="spain",
        categories=["Software", "Services"],
        daily_rate=300.50,
        status=SupplierStatus.ACTIVE
    )
    print(f"  ✓ Valid supplier created: {supplier.name}")
    
    # Test rate validation
    try:
        bad_supplier = SupplierCreate(
            name="Bad Supplier",
            country="spain",
            categories=["Software"],
            daily_rate=-100.00,
            status=SupplierStatus.ACTIVE
        )
        print("  ✗ Should reject negative rate")
        return False
    except ValueError:
        print("  ✓ Correctly rejected negative rate")
    
    # Test rate zero validation
    try:
        bad_supplier = SupplierCreate(
            name="Bad Supplier",
            country="spain",
            categories=["Software"],
            daily_rate=0.00,
            status=SupplierStatus.ACTIVE
        )
        print("  ✗ Should reject zero rate")
        return False
    except ValueError:
        print("  ✓ Correctly rejected zero rate")
    
    return True


def test_database():
    """Test database operations"""
    print("\n✓ Testing Database...")
    
    # Clear and seed
    clear_db()
    print("  ✓ Database cleared")
    
    count = seed_suppliers()
    print(f"  ✓ Seeded {count} suppliers")
    
    db = get_db()
    suppliers = db.all()
    
    if len(suppliers) != 5:
        print(f"  ✗ Expected 5 suppliers, got {len(suppliers)}")
        return False
    
    print(f"  ✓ Database contains {len(suppliers)} suppliers")
    
    # Verify structure
    supplier = suppliers[0]
    required_fields = ['name', 'country', 'categories', 'daily_rate', 'status', 'updated_at']
    for field in required_fields:
        if field not in supplier:
            print(f"  ✗ Missing field: {field}")
            return False
    
    print(f"  ✓ Supplier structure valid")
    
    # Test that categories are lists
    if not isinstance(supplier['categories'], list):
        print(f"  ✗ Categories should be list")
        return False
    
    if not supplier['categories']:
        print(f"  ✗ Categories list is empty")
        return False
    
    print(f"  ✓ Categories: {', '.join(supplier['categories'])}")
    
    # Test rate is positive
    if supplier['daily_rate'] <= 0:
        print(f"  ✗ Rate should be positive")
        return False
    
    print(f"  ✓ Rate: €{supplier['daily_rate']:.2f}")
    
    # Test status values
    valid_statuses = ['active', 'inactive']
    for s in suppliers:
        if s['status'] not in valid_statuses:
            print(f"  ✗ Invalid status: {s['status']}")
            return False
    
    print(f"  ✓ All status values valid")
    
    return True


def test_category_enum():
    """Test category enum values"""
    print("\n✓ Testing Category Enum...")
    
    valid_categories = [cat.value for cat in ProductCategory]
    expected = ["Software", "Hardware", "Services", "papeleria", "cafeteria"]
    
    if valid_categories != expected:
        print(f"  ✗ Categories mismatch")
        print(f"    Expected: {expected}")
        print(f"    Got: {valid_categories}")
        return False
    
    print(f"  ✓ Valid categories: {', '.join(valid_categories)}")
    return True


def test_status_enum():
    """Test status enum values"""
    print("\n✓ Testing Status Enum...")
    
    valid_statuses = [s.value for s in SupplierStatus]
    expected = ["active", "inactive"]
    
    if valid_statuses != expected:
        print(f"  ✗ Statuses mismatch")
        print(f"    Expected: {expected}")
        print(f"    Got: {valid_statuses}")
        return False
    
    print(f"  ✓ Valid statuses: {', '.join(valid_statuses)}")
    return True


def test_timestamps():
    """Test timestamp tracking"""
    print("\n✓ Testing Timestamps...")
    
    clear_db()
    
    supplier_data = {
        "name": "Time Test",
        "country": "spain",
        "categories": ["Services"],
        "daily_rate": 200.00,
        "status": "active",
        "updated_at": datetime.now().isoformat()
    }
    
    supplier = create_supplier(supplier_data)
    
    if 'updated_at' not in supplier:
        print("  ✗ updated_at field missing")
        return False
    
    # Verify it's a valid ISO format timestamp
    try:
        ts = datetime.fromisoformat(supplier['updated_at'])
        print(f"  ✓ Timestamp created: {supplier['updated_at']}")
    except:
        print(f"  ✗ Invalid timestamp format: {supplier['updated_at']}")
        return False
    
    return True


def main():
    print("=" * 60)
    print("  SUPPLIER MANAGEMENT — INTEGRATION TEST")
    print("=" * 60)
    
    tests = [
        ("Models", test_models),
        ("Category Enum", test_category_enum),
        ("Status Enum", test_status_enum),
        ("Database", test_database),
        ("Timestamps", test_timestamps),
    ]
    
    results = []
    for name, test_fn in tests:
        try:
            result = test_fn()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("  TEST RESULTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status} — {name}")
    
    print(f"\n  {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
