#!/usr/bin/env python3
"""
Servidor HTTP combinado que sirve HTML + API desde el mismo puerto
Esto evita problemas de CORS en Codespaces donde los puertos no se exponen automáticamente
"""
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import sys
from pathlib import Path

# Importar la API
sys.path.insert(0, str(Path(__file__).parent / 'services'))
from api.database import SuppliersDB

class CombinedHandler(SimpleHTTPRequestHandler):
    """Maneja tanto archivos estáticos como API"""
    
    db = None  # Instancia compartida de la DB
    
    @classmethod
    def set_db(cls, db_instance):
        cls.db = db_instance
    
    def do_GET(self):
        """GET: archivos estáticos o API"""
        if self.path.startswith('/api/'):
            self.handle_api_get()
        else:
            super().do_GET()
    
    def do_OPTIONS(self):
        """Manejo de CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def handle_api_get(self):
        """Maneja GET /api/suppliers"""
        try:
            if self.path == '/api/suppliers':
                suppliers = self.db.get_all_suppliers()
                # Agregar 'id' al resultado
                for supplier in suppliers:
                    if 'id' not in supplier:
                        supplier['id'] = supplier.doc_id if hasattr(supplier, 'doc_id') else None
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(suppliers).encode())
                print(f"✅ GET /api/suppliers → {len(suppliers)} proveedores")
            else:
                self.send_error(404)
        except Exception as e:
            print(f"❌ Error en API: {e}")
            self.send_error(500, str(e))
    
    def do_PATCH(self):
        """PATCH: actualizar estado o rating"""
        try:
            if '/api/suppliers/' in self.path:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                data = json.loads(body)
                
                # Extraer ID del path
                parts = self.path.split('/')
                supplier_id = int(parts[3])
                
                if '/status' in self.path:
                    self.db.update_status(supplier_id, data.get('status'))
                    print(f"✅ PATCH /api/suppliers/{supplier_id}/status → {data.get('status')}")
                elif '/rate' in self.path:
                    self.db.update_rate(supplier_id, data.get('rating'))
                    print(f"✅ PATCH /api/suppliers/{supplier_id}/rate → {data.get('rating')}")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok'}).encode())
            else:
                self.send_error(404)
        except Exception as e:
            print(f"❌ Error en PATCH: {e}")
            self.send_error(500, str(e))
    
    def do_DELETE(self):
        """DELETE: eliminar proveedor"""
        try:
            if '/api/suppliers/' in self.path:
                parts = self.path.split('/')
                supplier_id = int(parts[3])
                
                self.db.delete_supplier(supplier_id)
                print(f"✅ DELETE /api/suppliers/{supplier_id}")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'deleted'}).encode())
            else:
                self.send_error(404)
        except Exception as e:
            print(f"❌ Error en DELETE: {e}")
            self.send_error(500, str(e))
    
    def end_headers(self):
        """Agregar CORS headers a todas las respuestas"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

if __name__ == '__main__':
    os.chdir(Path(__file__).parent)
    
    # Inicializar DB
    db = SuppliersDB()
    CombinedHandler.set_db(db)
    
    PORT = 3000
    server = HTTPServer(('0.0.0.0', PORT), CombinedHandler)
    
    print(f"🚀 Servidor combinado iniciado en puerto {PORT}")
    print(f"   📁 Sirviendo archivos estáticos desde: {Path.cwd()}")
    print(f"   📡 API disponible en: http://localhost:3000/api/suppliers")
    print(f"   🌐 En Codespaces: https://cuddly-enigma-qvqjg4w7rx9g36x5r-3000.app.github.dev")
    print(f"   ✅ Interfaz: https://cuddly-enigma-qvqjg4w7rx9g36x5r-3000.app.github.dev/suppliers.html")
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️  Servidor detenido")
        db.close()
