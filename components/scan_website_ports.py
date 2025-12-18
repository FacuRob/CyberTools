import socket
import concurrent.futures
from typing import List, Dict, Optional, Tuple
import ipaddress
import time
import logging
import os
from functools import lru_cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortScanner:
    """Escáner de puertos optimizado con caché y timeouts dinámicos"""
    
    COMMON_PORTS = [
        80, 443, 8080, 8443,  # Web
        22, 21, 23, 25,       # Servicios básicos
        3306, 5432, 27017,    # Bases de datos
        3389, 5900, 6379      # Escritorio remoto y Redis
    ]
    
    # Servicios conocidos para detección rápida
    KNOWN_SERVICES = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
        53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP",
        443: "HTTPS", 3306: "MySQL", 5432: "PostgreSQL",
        6379: "Redis", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt",
        3389: "RDP", 5900: "VNC", 27017: "MongoDB"
    }
    
    def __init__(self, timeout: float = 1.5, max_workers: int = 100):
        """
        Configuración optimizada:
        - Timeout reducido: 1.5 segundos
        - Workers aumentados: 100 hilos
        - Caché de DNS habilitado
        """
        self.timeout = timeout
        self.max_workers = max_workers
        self.is_render = os.environ.get('RENDER', '').lower() == 'true'
        self._dns_cache = {}

    @lru_cache(maxsize=128)
    def validate_target(self, target: str) -> Tuple[bool, str]:
        """Validación optimizada con caché"""
        try:
            if not target or len(target) > 253:
                return False, "Target inválido"
            
            if any(c in target for c in " \t\n\r"):
                return False, "Target contiene espacios"
            
            # Verificar si es IP
            try:
                ipaddress.ip_address(target)
                return True, target
            except ValueError:
                pass
            
            # Validar dominio
            parts = target.split('.')
            if len(parts) < 2:
                return False, "Dominio debe tener al menos 2 partes"
            
            for part in parts:
                if not part or len(part) > 63:
                    return False, "Parte de dominio inválida"
                if not (part[0].isalnum() and part[-1].isalnum()):
                    return False, "Dominio debe comenzar/terminar con alfanumérico"
                    
            return True, target
        except Exception as e:
            return False, f"Error de validación: {str(e)}"

    def resolve_host(self, target: str) -> Tuple[bool, str]:
        """Resolución optimizada con caché"""
        # Verificar caché
        if target in self._dns_cache:
            return True, self._dns_cache[target]
        
        try:
            addr_info = socket.getaddrinfo(
                target, None, 
                socket.AF_UNSPEC,  # IPv4 o IPv6
                socket.SOCK_STREAM,
                0,
                socket.AI_ADDRCONFIG
            )
            ip = addr_info[0][4][0]
            
            # Guardar en caché
            self._dns_cache[target] = ip
            
            return True, ip
        except socket.gaierror as e:
            logger.error(f"DNS resolution failed for {target}: {e}")
            return False, f"No se pudo resolver {target}"
        except Exception as e:
            logger.error(f"Unexpected error resolving {target}: {e}")
            return False, f"Error: {str(e)}"

    def get_service_name(self, port: int) -> str:
        """Detección rápida de servicio"""
        return self.KNOWN_SERVICES.get(port, "unknown")

    def scan_port(self, ip: str, port: int) -> Dict:
        """Escaneo optimizado con timeout dinámico"""
        result = {
            "port": port,
            "open": False,
            "service": None,
            "response_time": None
        }
        
        # Determinar familia de socket
        try:
            sock_family = socket.AF_INET6 if ':' in ip else socket.AF_INET
        except Exception:
            return result
        
        # Timeout dinámico: puertos comunes más rápido
        timeout = self.timeout * 0.7 if port in self.KNOWN_SERVICES else self.timeout
        
        try:
            with socket.socket(sock_family, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                start = time.perf_counter()
                
                try:
                    s.connect((ip, port))
                    result["open"] = True
                    result["service"] = self.get_service_name(port)
                    result["response_time"] = f"{(time.perf_counter() - start)*1000:.1f}ms"
                except (socket.timeout, ConnectionRefusedError, OSError):
                    pass  # Puerto cerrado o filtrado
                    
        except Exception as e:
            logger.debug(f"Error scanning port {port}: {e}")
        
        return result

    def scan_ports(self, target: str, ports: Optional[List[int]] = None) -> Dict:
        """Escaneo paralelo optimizado"""
        # Validación
        is_valid, msg = self.validate_target(target)
        if not is_valid:
            return {"error": msg, "status": "invalid_target"}
        
        # Resolución DNS
        resolved, ip = self.resolve_host(target)
        if not resolved:
            return {"error": ip, "status": "resolution_failed"}
        
        # Configuración de puertos
        ports_to_scan = ports or self.COMMON_PORTS
        
        # Limitar en entornos restringidos
        if self.is_render and len(ports_to_scan) > 25:
            ports_to_scan = ports_to_scan[:25]
            logger.warning("Limitado a 25 puertos en Render")
        
        results = []
        start_time = time.perf_counter()
        
        # Escaneo paralelo con ThreadPoolExecutor optimizado
        try:
            workers = min(self.max_workers, len(ports_to_scan), 100)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_port = {
                    executor.submit(self.scan_port, ip, port): port 
                    for port in ports_to_scan
                }
                
                # Recopilar resultados con timeout global
                for future in concurrent.futures.as_completed(
                    future_to_port, 
                    timeout=len(ports_to_scan) * self.timeout + 5
                ):
                    try:
                        result = future.result(timeout=1)
                        if result["open"]:  # Solo guardar puertos abiertos
                            results.append(result)
                    except concurrent.futures.TimeoutError:
                        logger.warning(f"Timeout en puerto {future_to_port[future]}")
                    except Exception as e:
                        logger.error(f"Error procesando resultado: {e}")
        
        except Exception as e:
            logger.error(f"Error en escaneo paralelo: {e}")
            return {
                "error": f"Error en escaneo: {str(e)}",
                "status": "scan_failed"
            }
        
        # Ordenar por número de puerto
        results.sort(key=lambda x: x["port"])
        
        scan_duration = time.perf_counter() - start_time
        
        return {
            "status": "completed",
            "target": target,
            "ip": ip,
            "scanned_ports": len(ports_to_scan),
            "open_ports": results,
            "open_count": len(results),
            "scan_time": f"{scan_duration:.2f}s",
            "avg_time_per_port": f"{(scan_duration/len(ports_to_scan))*1000:.1f}ms",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }


def scan_website_ports(target: str, ports: Optional[List[int]] = None) -> Dict:
    """Interfaz pública del escáner optimizado"""
    try:
        scanner = PortScanner(timeout=1.5, max_workers=100)
        return scanner.scan_ports(target, ports)
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        return {
            "error": f"Error interno: {str(e)}",
            "status": "failed"
        }


# Test rápido
if __name__ == "__main__":
    result = scan_website_ports("google.com")
    print(f"\nResultados: {result.get('open_count', 0)} puertos abiertos")
    print(f"Tiempo: {result.get('scan_time', '?')}")
    for port in result.get('open_ports', []):
        print(f"  Puerto {port['port']}: {port['service']} ({port['response_time']})")