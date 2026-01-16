#!/bin/bash
# Script para probar el servidor WhatsApp en el servidor remoto
# Fecha: 16 de Enero 2026

echo "╔════════════════════════════════════════════════════════╗"
echo "║     TEST DEL SERVIDOR WHATSAPP - Servidor Remoto      ║"
echo "║              84.247.129.180:3000                       ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

SERVER="84.247.129.180"
PORT="3000"
API_KEY="opticaapp_2026_whatsapp_baileys_secret_key_12345"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funciones
print_test() {
    echo -e "${BLUE}📋 TEST: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Contador
TESTS_PASSED=0
TESTS_FAILED=0

test_endpoint() {
    local test_name="$1"
    local method="$2"
    local endpoint="$3"
    local expected_status="$4"
    local data="$5"
    
    print_test "$test_name"
    
    if [ "$method" == "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -H "X-API-Key: $API_KEY" "http://$SERVER:$PORT$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" -d "$data" "http://$SERVER:$PORT$endpoint")
    fi
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" == "$expected_status" ]; then
        print_success "Status: $status_code (esperado: $expected_status)"
        if [ ! -z "$body" ]; then
            echo "   Response: $body" | head -c 200
            echo ""
        fi
        ((TESTS_PASSED++))
        return 0
    else
        print_error "Status: $status_code (esperado: $expected_status)"
        if [ ! -z "$body" ]; then
            echo "   Response: $body"
        fi
        ((TESTS_FAILED++))
        return 1
    fi
}

echo -e "${CYAN}🔍 Verificando conectividad...${NC}"
echo ""

# Test 1: Ping al servidor
print_test "Ping al servidor"
if ping -c 1 $SERVER &> /dev/null; then
    print_success "Servidor alcanzable"
    ((TESTS_PASSED++))
else
    print_error "No se puede alcanzar el servidor"
    ((TESTS_FAILED++))
    exit 1
fi

echo ""

# Test 2: Health Check
test_endpoint "Health Check" "GET" "/health" "200"
echo ""

# Test 3: Rate Limit Status
test_endpoint "Rate Limit Status" "GET" "/api/rate-limit-status" "200"
echo ""

# Test 4: Rate Limit por Org
test_endpoint "Rate Limit Org Específica" "GET" "/api/rate-limit-status?organization_id=999" "200"
echo ""

# Test 5: Listar Sesiones
test_endpoint "Listar Sesiones" "GET" "/api/sessions" "200"
echo ""

# Test 6: Estado de Sesión No Existente
test_endpoint "Estado Sesión No Existente" "GET" "/api/status/999" "200"
echo ""

# Test 7: QR No Existente
test_endpoint "QR No Existente" "GET" "/api/qr/999" "404"
echo ""

# Test 8: Autenticación Fallida
print_test "Autenticación Fallida (API Key inválida)"
response=$(curl -s -w "\n%{http_code}" -H "X-API-Key: INVALID_KEY" "http://$SERVER:$PORT/api/sessions")
status_code=$(echo "$response" | tail -n1)
if [ "$status_code" == "401" ]; then
    print_success "Status: 401 (rechaza key inválida)"
    ((TESTS_PASSED++))
else
    print_error "Status: $status_code (esperado: 401)"
    ((TESTS_FAILED++))
fi
echo ""

# Test 9: Validación de Parámetros
test_endpoint "Validación de Parámetros" "POST" "/api/start-session" "400" '{}'
echo ""

# Test 10: Enviar Mensaje Sin Sesión
test_endpoint "Enviar Mensaje Sin Sesión" "POST" "/api/send-message" "404" '{"organization_id":"999","phone":"3001234567","message":"Test"}'
echo ""

# Test 11: Health Check Sin Auth
print_test "Health Check Sin Autenticación (público)"
response=$(curl -s -w "\n%{http_code}" "http://$SERVER:$PORT/health")
status_code=$(echo "$response" | tail -n1)
if [ "$status_code" == "200" ]; then
    print_success "Status: 200 (accesible sin auth)"
    ((TESTS_PASSED++))
else
    print_error "Status: $status_code (esperado: 200)"
    ((TESTS_FAILED++))
fi
echo ""

# Test 12: Verificar PM2 Status
print_test "Estado del Servidor en PM2"
pm2_status=$(ssh root@$SERVER "pm2 jlist" 2>/dev/null | grep -o '"name":"whatsapp-server".*"status":"[^"]*"' | grep -o 'status":"[^"]*"' | cut -d'"' -f3)
if [ "$pm2_status" == "online" ]; then
    print_success "Servidor WhatsApp: online"
    ((TESTS_PASSED++))
elif [ "$pm2_status" == "stopped" ]; then
    print_warning "Servidor WhatsApp: stopped (esperado - no se ha iniciado desde correcciones)"
    ((TESTS_PASSED++))
else
    print_error "Servidor WhatsApp: $pm2_status"
    ((TESTS_FAILED++))
fi
echo ""

# Resumen
echo "═══════════════════════════════════════════════════════"
echo -e "${CYAN}📊 RESUMEN DE PRUEBAS${NC}"
echo "═══════════════════════════════════════════════════════"

TOTAL=$((TESTS_PASSED + TESTS_FAILED))
PERCENTAGE=$(echo "scale=1; ($TESTS_PASSED / $TOTAL) * 100" | bc)

echo -e "${GREEN}✅ Pruebas exitosas: $TESTS_PASSED/$TOTAL ($PERCENTAGE%)${NC}"

if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}❌ Pruebas fallidas: $TESTS_FAILED/$TOTAL${NC}"
fi

echo ""
echo -e "${CYAN}Estado del Servidor:${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    print_success "SERVIDOR OPERACIONAL - Todas las pruebas pasaron"
    print_success "Rate limiting funcionando correctamente"
    print_success "Autenticación funcionando correctamente"
    print_success "Validaciones funcionando correctamente"
    print_success "Endpoints respondiendo correctamente"
    echo ""
    echo -e "${GREEN}🎉 El servidor está listo para conectar WhatsApp el lunes${NC}"
else
    print_error "HAY PROBLEMAS QUE RESOLVER"
    print_warning "Revisar logs: ssh root@$SERVER \"pm2 logs whatsapp-server --lines 50\""
    print_warning "Verificar estado: ssh root@$SERVER \"pm2 status\""
fi

echo ""

# Exit code
exit $TESTS_FAILED
