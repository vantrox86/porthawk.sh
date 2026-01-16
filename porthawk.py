#!/usr/bin/env python3
"""
Port Scanner v2.0 - Scanner de Portas Profissional
Autor: Romildo (thuf) - helptecinfo.com
"""

import socket
import pyfiglet
import argparse
import time
import json
import signal
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from tqdm import tqdm
from colorama import Fore, Style, init

# Inicializar colorama
init(autoreset=True)

class ProfessionalPortScanner:
    """Scanner de portas TCP profissional com interface híbrida (CLI + Interativa)"""
    
    def __init__(self):
        self.script_info = "Romildo (thuf) - foryousec.com"
        self.services = {
            20: "FTP-Data", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
            53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS",
            993: "IMAPS", 995: "POP3S", 1723: "PPTP", 3306: "MySQL",
            3389: "RDP", 5432: "PostgreSQL", 5900: "VNC", 8080: "HTTP-Proxy"
        }
        self.open_ports = []
        self.stop_scanning = False
        self.start_time = None
        self.target_ip = None
        
    def print_banner(self):
        """Banner profissional colorido"""
        print(f"\n{Fore.CYAN}{'='*60}")
        banner = pyfiglet.figlet_format("SCANNER PORTHAWK", font="slant", width=55)
        print(f"{Fore.WHITE}{banner}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}v2.0 - {self.script_info}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    def interactive_input(self, prompt, default=None, port=False, validate_func=None):
        """Input interativo colorido com defaults e validação"""
        default_str = f" [{default}]" if default is not None else ""
        color = Fore.CYAN if not port else Fore.YELLOW
        while True:
            value = input(f"{color}{prompt}{default_str}: {Style.RESET_ALL}").strip()
            
            if not value and default is not None:
                return default
            
            if port:
                try:
                    val = int(value)
                    if validate_func and not validate_func(val):
                        print(f"{Fore.RED}❌ Valor inválido. Tente novamente.{Style.RESET_ALL}")
                        continue
                    return val
                except ValueError:
                    print(f"{Fore.RED}❌ Porta deve ser número (1-65535){Style.RESET_ALL}")
                    continue
            return value
    
    def resolve_target(self, target):
        """Resolve hostname para IP com validação"""
        try:
            resolved = socket.gethostbyname(target)
            print(f"{Fore.GREEN}✓ Target resolvido: {target} → {resolved}{Style.RESET_ALL}")
            return resolved
        except socket.gaierror as e:
            print(f"{Fore.RED}❌ Erro de resolução DNS: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[!] Usando IP literal: {target}{Style.RESET_ALL}")
            return target
    
    def validate_single_port(self, port):
        """Valida porta única (1-65535)"""
        return 1 <= port <= 65535
    
    def validate_ports_range(self, start, end):
        """Valida range de portas"""
        if not (1 <= start <= 65535 and 1 <= end <= 65535):
            raise ValueError("Portas devem estar entre 1-65535")
        if start > end:
            raise ValueError("Porta inicial deve ser <= porta final")
        return start, end
    
    def signal_handler(self, sig, frame):
        """Graceful shutdown"""
        self.stop_scanning = True
        print(f"\n{Fore.YELLOW}⏹️ Scan interrompido. Salvando resultados parciais...{Style.RESET_ALL}")
        self.print_summary()
        sys.exit(0)
    
    def scan_single_port(self, target_ip, port, timeout):
        """Scan individual com retry"""
        for attempt in range(2):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(timeout)
                    result = sock.connect_ex((target_ip, port))
                    if result == 0:
                        return port
                    time.sleep(0.005 * attempt)
            except:
                pass
        return None
    
    def get_service_name(self, port):
        """Retorna nome do serviço"""
        return self.services.get(port, "Unknown")
    
    def calculate_workers(self, port_range):
        """Workers dinâmicos baseados no range"""
        return min(1000, max(50, port_range // 8))
    
    def scan_target(self, target_ip, start_port, end_port, timeout):
        """Scan principal multithreaded"""
        self.start_time = time.time()
        port_range = end_port - start_port + 1
        workers = self.calculate_workers(port_range)
        
        print(f"{Fore.GREEN}🔍 Iniciando scan: {target_ip}:{start_port}-{end_port}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}⚙️ Workers: {workers} | Timeout: {timeout}s | Portas: {port_range:,}{Style.RESET_ALL}\n")
        
        try:
            with ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_port = {
                    executor.submit(self.scan_single_port, target_ip, port, timeout): port
                    for port in range(start_port, end_port + 1)
                }
                
                with tqdm(total=len(future_to_port), 
                          desc="🔎 Scanning", 
                          unit="port",
                          bar_format="{l_bar}%s{bar}%s | {n_fmt}/{total_fmt} | {rate_fmt}" % 
                          (Fore.BLUE, Fore.WHITE),
                          colour="green") as pbar:
                    
                    for future in as_completed(future_to_port):
                        if self.stop_scanning:
                            break
                        
                        result = future.result()
                        if result:
                            self.open_ports.append(result)
                            service = self.get_service_name(result)
                            print(f"{Fore.GREEN}✅ {result:5d} | {service:<12} | TCP{Style.RESET_ALL}")
                        
                        pbar.update(1)
                        
        except KeyboardInterrupt:
            self.signal_handler(None, None)
    
    def print_summary(self):
        """Relatório final profissional"""
        duration = time.time() - self.start_time if self.start_time else 0
        rate = len(self.open_ports) / duration if duration > 0 else 0
        
        print(f"\n{Fore.MAGENTA}{'='*65}")
        print(f"📊 RELATÓRIO FINAL - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{Fore.MAGENTA}{'='*65}{Style.RESET_ALL}")
        
        if self.open_ports:
            self.open_ports.sort()
            print(f"{Fore.GREEN}🎉 {len(self.open_ports)} porta(s) ABERTA(S) em {duration:.1f}s")
            print(f"{Fore.BLUE}📈 Velocidade: {rate:.0f} portas/segundo{Style.RESET_ALL}")
            
            print(f"\n{Fore.YELLOW}📋 PORTAS ABERTAS:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'-'*45}{Style.RESET_ALL}")
            for port in self.open_ports:
                service = self.get_service_name(port)
                print(f"  {Fore.GREEN}{port:5d}{Style.RESET_ALL} │ {Fore.CYAN}{service:<12}{Style.RESET_ALL} │ TCP")
        else:
            print(f"{Fore.RED}😴 Nenhuma porta aberta encontrada ({duration:.1f}s){Style.RESET_ALL}")
        
        print(f"{Fore.MAGENTA}{'='*65}{Style.RESET_ALL}")
    
    def save_report(self, filename):
        """Salva relatórios JSON e TXT"""
        if not self.open_ports:
            print(f"{Fore.YELLOW}ℹ️ Nenhuma porta aberta para salvar{Style.RESET_ALL}")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{filename}_{timestamp}" if filename else f"scan_{timestamp}"
        
        data = {
            "target": self.target_ip,
            "scan_date": datetime.now().isoformat(),
            "duration_seconds": time.time() - self.start_time,
            "ports_scanned": self.end_port - self.start_port + 1,
            "open_ports": self.open_ports,
            "services_detected": {p: self.get_service_name(p) for p in self.open_ports}
        }
        
        # JSON
        json_file = f"{base_name}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # TXT
        txt_file = f"{base_name}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"PORT SCANNER v2.0 - RELATÓRIO\n")
            f.write(f"{'='*50}\n\n")
            f.write(f"Target: {self.target_ip}\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Duração: {data['duration_seconds']:.1f}s\n")
            f.write(f"Portas escaneadas: {data['ports_scanned']:,}\n")
            f.write(f"Portas abertas: {len(self.open_ports)}\n\n")
            f.write(f"PORTA  | SERVIÇO     | STATUS\n")
            f.write(f"-------|-------------|--------\n")
            for port in sorted(self.open_ports):
                f.write(f"{port:5d}  | {self.get_service_name(port):<11} | ABERTA\n")
        
        print(f"{Fore.GREEN}💾 Relatórios salvos:{Style.RESET_ALL}")
        print(f"   📄 TXT:  {txt_file}")
        print(f"   📊 JSON: {json_file}")
    
    def interactive_mode(self):
        """MODO INTERATIVO MELHORADO - Com opção de portas comuns!"""
        self.print_banner()
        
        # 1. Target
        target = self.interactive_input("🎯 IP ou hostname", "scanme.nmap.org")
        self.target_ip = self.resolve_target(target)
        
        # 2. Opção de portas especiais
        print(f"\n{Fore.CYAN}📋 Opções de portas pré-configuradas:{Style.RESET_ALL}")
        print(f"  1 = {Fore.GREEN}1-1024 (padrão){Style.RESET_ALL}")
        print(f"  2 = {Fore.GREEN}Web (80,443,8080){Style.RESET_ALL}")
        print(f"  3 = {Fore.GREEN}Servidores (1-10000){Style.RESET_ALL}")
        print(f"  4 = {Fore.GREEN}Completo (1-65535){Style.RESET_ALL}")
        print(f"  0 = {Fore.YELLOW}Personalizado{Style.RESET_ALL}")
        
        port_option = self.interactive_input("🔢 Escolha opção de portas", "1", port=True)
        
        # Configurar portas baseado na opção
        if port_option == "2":  # Web
            self.start_port, self.end_port = 80, 8080
            print(f"{Fore.GREEN}✓ Modo WEB selecionado: portas 80-8080{Style.RESET_ALL}")
        elif port_option == "3":  # Servidores
            self.start_port, self.end_port = 1, 10000
            print(f"{Fore.GREEN}✓ Modo SERVIDORES: portas 1-10000{Style.RESET_ALL}")
        elif port_option == "4":  # Completo
            self.start_port, self.end_port = 1, 65535
            print(f"{Fore.GREEN}✓ Modo COMPLETO: portas 1-65535 (pode demorar!){Style.RESET_ALL}")
        elif port_option == "0":  # Personalizado
            start_port = self.interactive_input("📈 Porta inicial", "1", port=True, validate_func=self.validate_single_port)
            end_port = self.interactive_input("📈 Porta final", "1024", port=True, validate_func=self.validate_single_port)
            self.start_port, self.end_port = self.validate_ports_range(start_port, end_port)
        else:  # Padrão 1-1024
            self.start_port, self.end_port = 1, 1024
            print(f"{Fore.GREEN}✓ Modo PADRÃO: portas 1-1024{Style.RESET_ALL}")
        
        # 3. Timeout
        timeout = self.interactive_input("⏱️ Timeout (segundos)", "0.5")
        try:
            timeout = float(timeout)
            if timeout <= 0:
                timeout = 0.5
        except ValueError:
            timeout = 0.5
        
        # 4. Confirmar
        print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        print(f"🎯 Target: {self.target_ip}")
        print(f"📈 Portas: {self.start_port}-{self.end_port}")
        print(f"⏱️ Timeout: {timeout}s")
        confirm = self.interactive_input("🚀 Iniciar scan? (s/N)", "s").lower()
        
        if confirm not in ['s', 'sim', 'y', 'yes']:
            print(f"{Fore.YELLOW}👋 Scan cancelado!{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}🚀 Iniciando em 3... 2... 1...{Style.RESET_ALL}")
        time.sleep(3)
        
        # 5. SCAN!
        signal.signal(signal.SIGINT, self.signal_handler)
        self.scan_target(self.target_ip, self.start_port, self.end_port, timeout)
        self.print_summary()
        
        # 6. Salvar?
        if self.open_ports:
            save = self.interactive_input("💾 Salvar relatório? (s/N)", "s").lower()
            if save in ['s', 'sim', 'y', 'yes']:
                filename = self.interactive_input("📁 Nome do arquivo", f"scan_{self.target_ip.replace('.','_')}")
                self.save_report(filename)
    
    def cli_mode(self, args):
        """MODO CLI para automação"""
        self.print_banner()
        self.target_ip = self.resolve_target(args.target)
        
        try:
            self.start_port, self.end_port = self.validate_ports_range(args.start, args.end)
        except ValueError as e:
            print(f"{Fore.RED}❌ {e}{Style.RESET_ALL}")
            return
        
        signal.signal(signal.SIGINT, self.signal_handler)
        self.scan_target(self.target_ip, self.start_port, self.end_port, args.timeout)
        self.print_summary()
        
        if args.output and self.open_ports:
            self.save_report(args.output)
    
    def run(self):
        """Executa no modo correto"""
        parser = argparse.ArgumentParser(
            description="""🛡️ Port Scanner v2.0 - Profissional e Fácil de Usar

Interativo: python port_scanner.py
CLI: python port_scanner.py IP -s 1 -e 1024""",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument("target", nargs='?', help="IP/hostname")
        parser.add_argument("-s", "--start", type=int, default=1, help="Porta inicial")
        parser.add_argument("-e", "--end", type=int, default=1024, help="Porta final")
        parser.add_argument("-t", "--timeout", type=float, default=0.5, help="Timeout (s)")
        parser.add_argument("-o", "--output", help="Arquivo de saída")
        
        args = parser.parse_args()
        
        if args.target:
            self.cli_mode(args)
        else:
            self.interactive_mode()

def main():
    try:
        scanner = ProfessionalPortScanner()
        scanner.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Até logo!{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}💥 Erro: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()
