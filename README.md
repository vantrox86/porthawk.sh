# 🛡️ PortHawk – Professional Port Scanner v2.0

Scanner de portas TCP **profissional**, rápido e interativo, desenvolvido em Python, com suporte a **modo CLI**, **modo interativo**, **multithreading**, **barra de progresso**, **relatórios** e **interface visual colorida**.

Autor: **Romildo (thuf)**  
Website: **https://foryousec.com**


## 📌 Visão Geral

O **PortHawk** é um scanner de portas TCP projetado para profissionais de **cibersegurança**, **pentesters**, **analistas de redes** e **estudantes avançados**, oferecendo:

- Interface **interativa amigável**
- Modo **CLI para automação**
- **Multithreading inteligente**
- Detecção de **serviços comuns**
- Relatórios em **TXT e JSON**
- Encerramento seguro (graceful shutdown)
- Barra de progresso com **tqdm**
- Interface colorida (Colorama)


## ⚙️ Funcionalidades

- Scan TCP de portas **customizado ou pré-configurado**
- Resolução automática de hostname → IP
- Modos rápidos:
  - 1–1024 (padrão)
  - Web (80–8080)
  - Servidores (1–10000)
  - Completo (1–65535)
- Controle de **timeout**
- Exibição em tempo real das portas abertas
- Relatório final com estatísticas
- Exportação dos resultados


## 🧰 Requisitos

- **Python 3.8+**
- Linux / WSL / macOS / Windows
- Permissão de execução no arquivo


## 📦 Instalação

### 1️⃣ Clonar o repositório

```bash
git clone https://github.com/seuusuario/porthawk.git
cd porthawk
```


### 2️⃣ Criar ambiente virtual (opcional, recomendado)

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3️⃣ Instalar dependências

#### Instalação via pip

```bash
pip install pyfiglet tqdm colorama
```

#### Ou via requirements.txt

```bash
pip install -r requirements.txt
```

📄 **requirements.txt**

```txt
pyfiglet
tqdm
colorama
```


### 4️⃣ Permissão de execução

```bash
chmod +x port_scanner.py
```

## 🚀 Como Usar

### 🔹 Modo Interativo

```bash
python3 port_scanner.py
```

---

### 🔹 Modo CLI (Automação)

```bash
python3 port_scanner.py scanme.nmap.org -s 1 -e 1024 -t 0.5 -o resultado_scan
```

#### Parâmetros disponíveis

| Parâmetro | Descrição |
|----------|----------|
| `target` | IP ou hostname |
| `-s` | Porta inicial |
| `-e` | Porta final |
| `-t` | Timeout (segundos) |
| `-o` | Arquivo de saída |

---

## 📊 Relatórios

Arquivos gerados automaticamente:

- `.txt` – leitura humana
- `.json` – integração e automação

Exemplo:

```text
scan_192_168_1_1_20260116_143210.txt
scan_192_168_1_1_20260116_143210.json
```


## 📈 Exemplo de Saída

```text
✅  22 | SSH          | TCP
✅  80 | HTTP         | TCP
✅ 443 | HTTPS        | TCP

🎉 3 portas abertas em 1.2s
📈 Velocidade: 850 portas/segundo
```


## ⚠️ Aviso Legal

Este projeto é destinado **exclusivamente para fins educacionais e testes autorizados**.

> **Nunca execute scans sem autorização explícita.**  
> O autor não se responsabiliza por uso indevido.


## 🧠 Roadmap

- Scan UDP
- Banner Grabbing
- Exportação CSV
- Integração com Nmap
- Fingerprinting de serviços

