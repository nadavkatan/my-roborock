## My-Roborock

This repo contains two parts:

1. **Node.js Backend** (`server.js`)  
   - Provides a REST API to send commands to a Roborock vacuum over LAN using its token and IP.  

2. **Python Helper Script** (`decrypt-rc4/`)  
    - A small tool to decrypt MiOT RC4-encrypted responses captured from network traffic.  
    - Used once to extract the LAN token, which is then configured in `.env`.

