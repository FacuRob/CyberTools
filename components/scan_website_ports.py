import socket
import concurrent.futures
from typing import List, Dict, Optional, Tuple
import ipaddress
import time
import logging
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortScanner:
    """Versión mejorada del escáner de puertos con soporte IPv4/IPv6"""
    
    COMMON_PORTS = [
        80, 443, 8080, 8443,  # Puertos web comunes
        22, 21, 23,           # Puertos de servicios
        3306, 5432,          # Bases de datos
        3389, 5900           # Escritorio remoto
    ]
    
    def __init__(self, timeout: float = 2.0, max_workers: int = 50):
        """
        Configuración optimizada:
        - Timeout: 2 segundos
        - Workers: 50 hilos máximo
        """
        self.timeout = timeout
        self.max_workers = max_workers
        self.is_render = os.environ.get('RENDER', '').lower() == 'true'

    def validate_target(self, target: str) -> Tuple[bool, str]:
        """Validación mejorada del target"""
        try:
            if not target or len(target) > 253:
                return False, "Target inválido"
            
            # Verificar formato básico
            if any(c in target for c in " \t\n\r"):
                return False, "Target contiene espacios"
                
            # Verificar si es IP
            try:
                ipaddress.ip_address(target)
                return True, target
            except ValueError:
                pass
                
            # Verificar formato de dominio
            if not all(part.isalnum() or part == '-' for part in target.split('.')):
                return False, "Dominio inválido"
                
            return True, target
        except Exception as e:
            return False, f"Error de validación: {str(e)}"

    def resolve_host(self, target: str) -> Tuple[bool, str]:
        """Resolución con soporte IPv6"""
        try:
            # Usar getaddrinfo que soporta ambos protocolos
            addr_info = socket.getaddrinfo(target, None)
            return True, addr_info[0][4][0]
        except (socket.gaierror, IndexError) as e:
            logger.error(f"Error resolviendo {target}: {str(e)}")
            return False, f"No se pudo resolver {target}"
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return False, f"Error resolviendo host: {str(e)}"

    def scan_port(self, ip: str, port: int) -> Dict:
        """Escaneo compatible con IPv4/IPv6"""
        result = {
            "port": port,
            "open": False,
            "error": None,
            "service": None,
            "response_time": None
        }
        
        # Determinar familia de sockets según la IP
        try:
            if ':' in ip:  # IPv6
                sock_family = socket.AF_INET6
            else:  # IPv4
                sock_family = socket.AF_INET
        except Exception as e:
            result["error"] = f"Error determinando familia IP: {str(e)}"
            return result
        
        try:
            with socket.socket(sock_family, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                
                start = time.time()
                try:
                    s.connect((ip, port))
                    result["open"] = True
                    try:
                        result["service"] = socket.getservbyport(port)
                    except:
                        result["service"] = "unknown"
                except (socket.timeout, ConnectionRefusedError, BlockingIOError, OSError) as e:
                    if isinstance(e, ConnectionRefusedError):
                        result["error"] = "Connection refused"
                    elif isinstance(e, socket.timeout):
                        result["error"] = "Timeout"
                    else:
                        result["error"] = str(e)
                except Exception as e:
                    result["error"] = f"Unexpected error: {str(e)}"
                
                result["response_time"] = f"{(time.time() - start)*1000:.2f}ms"
                
        except Exception as e:
            result["error"] = f"Socket error: {str(e)}"
        
        return result

    def scan_ports(self, target: str, ports: Optional[List[int]] = None) -> Dict:
        """Versión optimizada con mejor reporte de resultados"""
        # Validación
        is_valid, msg = self.validate_target(target)
        if not is_valid:
            return {"error": msg, "status": "invalid_target"}
        
        # Resolución
        resolved, ip = self.resolve_host(target)
        if not resolved:
            return {"error": ip, "status": "resolution_failed"}
        
        # Configuración de puertos
        ports_to_scan = ports or self.COMMON_PORTS
        
        # Limitar puertos en Render
        if self.is_render and len(ports_to_scan) > 20:
            ports_to_scan = ports_to_scan[:20]
            logger.warning("Render Free Tier: Limitado a 20 puertos")
        
        results = []
        start_time = time.time()
        
        try:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=min(self.max_workers, len(ports_to_scan))
            ) as executor:
                futures = {executor.submit(self.scan_port, ip, port): port for port in ports_to_scan}
                
                for future in concurrent.futures.as_completed(futures):
                    try:
                        results.append(future.result())
                    except Exception as e:
                        logger.error(f"Error en thread: {str(e)}")
                        results.append({
                            "port": futures[future],
                            "open": False,
                            "error": str(e),
                            "service": None
                        })
        
        except Exception as e:
            logger.error(f"Error en ThreadPool: {str(e)}")
            return {
                "error": f"Error en escaneo: {str(e)}",
                "status": "scan_failed"
            }
        
        # Procesar resultados
        open_ports = [r for r in results if r["open"]]
        closed_ports = [r for r in results if not r["open"]]
        
        return {
            "status": "completed",
            "target": target,
            "ip": ip,
            "scanned_ports": len(ports_to_scan),
            "open_ports": open_ports,
            "closed_ports": closed_ports if len(closed_ports) < 10 else [],
            "scan_time": f"{time.time() - start_time:.2f}s",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }


def scan_website_ports(target: str, ports: Optional[List[int]] = None) -> Dict:
    """Interfaz mejorada para el escáner"""
    try:
        scanner = PortScanner()
        return scanner.scan_ports(target, ports)
    except Exception as e:
        logger.error(f"Error fatal en scan_website_ports: {str(e)}")
        return {
            "error": f"Error interno: {str(e)}",
            "status": "failed"
        }