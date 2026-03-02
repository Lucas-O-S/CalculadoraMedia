# CalculadoraMedia

## Rodar em outro dispositivo

1. **Ter Python 3.11**  
   Instale em [python.org](https://www.python.org/downloads/) ou Microsoft Store. No Windows, o comando `py -3.11` deve funcionar.

2. **Copiar o projeto**  
   Clone o repositório ou copie a pasta do projeto (sem a pasta `.venv`, ela não vai no Git).

3. **Criar o ambiente e instalar dependências**  
   Abra o terminal na pasta do projeto e rode:

   **Windows (PowerShell):**
   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

   **Linux / macOS:**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Rodar o app**
   ```bash
   python main.py
   ```
   Ou no Cursor/VS Code: abra a pasta, selecione o interpretador `.venv` e execute `main.py`.

---

## Configuração do venv (detalhes)

O projeto usa ambiente virtual (`.venv`). Use o **Python do Windows** (python.org ou Microsoft Store); o Python do MSYS2 costuma falhar ao instalar pandas.

Para **recriar** o venv no Windows (PowerShell):

```powershell
Remove-Item -Recurse -Force .venv
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

No Cursor/VS Code: selecione o interpretador **Python 3.11** em `.venv\Scripts\python.exe` (Windows) ou `.venv/bin/python` (Linux/Mac).