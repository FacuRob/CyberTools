import socket
import concurrent.futures
from typing import List, Tuple
import ipaddress
import time

class PortScanner:
    """Clase para escanear puertos de un sitio web o dirección IP de manera eficiente."""
    
    COMMON_PORTS = [
        20, 21, 22, 23, 25, 53, 80, 110, 135, 139, 
        143, 443, 445, 3389, 8080, 8443, 3306, 5432,
        27017, 6379, 11211, 9200
    ]
    
    def __init__(self, timeout: float = 1.0, max_workers: int = 100):
        """
        Inicializa el escáner de puertos.
        
        Args:
            timeout: Tiempo de espera para la conexión a cada puerto (en segundos)
            max_workers: Número máximo de hilos para escaneo concurrente
        """
        self.timeout = timeout
        self.max_workers = max_workers
    
    def validate_target(self, target: str) -> Tuple[bool, str]:
        """Valida el objetivo de escaneo."""
        if not target:
            return False, "Error: No se proporcionó un objetivo para el escaneo."
        
        if not isinstance(target, str) or len(target) > 255:
            return False, "Error: Objetivo inválido."
        
        # Verificar si es una dirección IP válida
        try:
            ipaddress.ip_address(target)
            return True, target
        except ValueError:
            pass  # No es una IP, podría ser un hostname
        
        return True, target
    
    def resolve_host(self, target: str) -> Tuple[bool, str]:
        """Resuelve el hostname a una dirección IP."""
        try:
            ip_address = socket.gethostbyname(target)
            return True, ip_address
        except socket.gaierror:
            return False, f"Error: No se pudo resolver el host '{target}'. Verifica la dirección o conexión."
        except Exception as e:
            return False, f"Error inesperado al resolver el host: {e}"
    
    def scan_port(self, ip_address: str, port: int) -> Tuple[int, bool, str]:
        """Escanea un puerto individual."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                result_code = sock.connect_ex((ip_address, port))
                if result_code == 0:
                    try:
                        service = socket.getservbyport(port)
                    except:
                        service = "desconocido"
                    return port, True, service
                return port, False, ""
        except Exception as e:
            return port, False, f"Error: {str(e)}"
    
    def scan_ports(self, target: str, ports: List[int] = None) -> str:
        """
        Escanea los puertos especificados de un objetivo.
        
        Args:
            target: Dirección IP o hostname a escanear
            ports: Lista de puertos a escanear (opcional, usa los comunes por defecto)
        
        Returns:
            String formateado con los resultados del escaneo
        """
        # Validación del objetivo
        is_valid, validation_msg = self.validate_target(target)
        if not is_valid:
            return validation_msg
        
        # Resolución del host
        resolved, host_msg = self.resolve_host(target)
        if not resolved:
            return host_msg
        
        ip_address = host_msg
        ports_to_scan = ports or self.COMMON_PORTS
        
        # Preparar resultados
        results = [
            f"\n[+] Escaneo de puertos iniciado: {target}",
            f"[+] Dirección IP resuelta: {ip_address}",
            f"[+] Puertos a escanear: {len(ports_to_scan)}",
            f"[+] Tiempo de espera por puerto: {self.timeout}s",
            "[+] Escaneo en progreso...\n"
        ]
        
        open_ports = []
        start_time = time.time()
        
        # Escaneo concurrente de puertos
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.scan_port, ip_address, port): port 
                for port in ports_to_scan
            }
            
            for future in concurrent.futures.as_completed(futures):
                port, is_open, service_or_error = future.result()
                if is_open:
                    open_ports.append(port)
                    results.append(f"  [+] Puerto {port}/tcp ({service_or_error}): Abierto")
                else:
                    if service_or_error:  # Hubo un error
                        results.append(f"  [!] Puerto {port}/tcp: Error ({service_or_error})")
        
        # Resumen del escaneo
        scan_duration = time.time() - start_time
        results.append("\n[+] Resumen del escaneo:")
        results.append(f"  - Tiempo total: {scan_duration:.2f} segundos")
        results.append(f"  - Puertos abiertos encontrados: {len(open_ports)}")
        
        if open_ports:
            results.append("  - Lista de puertos abiertos:")
            for port in sorted(open_ports):
                results.append(f"    * {port}/tcp")
        else:
            results.append("  - No se encontraron puertos abiertos.")
        
        results.append("\n[+] Escaneo completado.")
        
        return "\n".join(results)


def scan_website_ports(target: str, ports: List[int] = None) -> str:
    """
    Función conveniente para escanear puertos sin necesidad de instanciar la clase.
    
    Args:
        target: Dirección IP o hostname a escanear
        ports: Lista opcional de puertos a escanear (usa los comunes por defecto)
    
    Returns:
        String formateado con los resultados del escaneo
    """
    scanner = PortScanner()
    return scanner.scan_ports(target, ports)