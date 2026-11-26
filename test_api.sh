#!/bin/bash

# Nexova API - Complete Authentication Test Script
# Tests all endpoints and authentication flows

set -e

BASE_URL="http://localhost:8000"
echo "Nexova API Test Suite"
echo "====================="
echo "API Base URL: $BASE_URL"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0

test_endpoint() {
    local test_name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local token=$5
    local expected_status=$6
    
    echo -n "Testing: $test_name... "
    
    if [ -z "$token" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint" \
            ${data:+-H "Content-Type: application/json" -d "$data"})
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint" \
            -H "Authorization: Bearer $token" \
            ${data:+-H "Content-Type: application/json" -d "$data"})
    fi
    
    status_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)
    
    if [[ "$status_code" == "$expected_status"* ]]; then
        echo -e "${GREEN}✓ PASSED${NC} (Status: $status_code)"
        ((PASSED++))
        echo "$body"
    else
        echo -e "${RED}✗ FAILED${NC} (Expected: $expected_status, Got: $status_code)"
        ((FAILED++))
        echo "$body"
    fi
    echo ""
}

# Test 1: Health check
test_endpoint "Health check" "GET" "/health" "" "" "200"

# Test 2: Register user bob@example.com
echo "--- User Registration ---"
register_response=$(curl -s -X POST "$BASE_URL/users" \
    -H "Content-Type: application/json" \
    -d '{
        "email":"bob@example.com",
        "password":"SecurePass123",
        "name":"Bob Johnson",
        "phone":"+1-555-0102",
        "address":"456 Oak Ave"
    }')

USER_ID=$(echo "$register_response" | python -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
echo "✓ Registered user: bob@example.com (ID: $USER_ID)"
echo ""

# Test 3: Login and get token
echo "--- Authentication ---"
login_response=$(curl -s -X POST "$BASE_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"bob@example.com","password":"SecurePass123"}')

TOKEN=$(echo "$login_response" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
echo "✓ Login successful, token received"
echo ""

# Test 4: Protected endpoints with valid token
echo "--- Protected Endpoints ---"
test_endpoint "GET /auth/me" "GET" "/auth/me" "" "$TOKEN" "200"
test_endpoint "GET /users" "GET" "/users" "" "$TOKEN" "200"
test_endpoint "GET /users/$USER_ID" "GET" "/users/$USER_ID" "" "$TOKEN" "200"
test_endpoint "GET /profiles/me" "GET" "/profiles/me" "" "$TOKEN" "200"

# Test 5: Update profile
test_endpoint "PUT /profiles/me" "PUT" "/profiles/me" \
    '{"name":"Bob J. Johnson","phone":"+1-555-0103"}' "$TOKEN" "200"

# Test 6: Error cases
echo "--- Error Handling ---"
test_endpoint "Protected endpoint without token" "GET" "/users" "" "" "403"
test_endpoint "Invalid email format" "POST" "/users" \
    '{"email":"invalid","password":"SecurePass123"}' "" "422"
test_endpoint "Duplicate email registration" "POST" "/users" \
    '{"email":"bob@example.com","password":"OtherPass123","name":"Fake"}' "" "400"
test_endpoint "Wrong password login" "POST" "/auth/login" \
    '{"email":"bob@example.com","password":"WrongPassword"}' "" "401"
test_endpoint "Invalid token format" "GET" "/users" "" "invalid.token" "401"

# Summary
echo ""
echo "======================================"
echo "Test Summary"
echo "======================================"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
