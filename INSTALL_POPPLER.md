# Installing Poppler on Windows

Poppler is required for pdf2image to work properly. Here's how to install it:

## Option 1: Quick Install (Recommended)

1. **Download Poppler for Windows**:
   - Go to: https://github.com/oschwartz10612/poppler-windows/releases/
   - Download the latest `Release-XX.XX.X-X.zip` file

2. **Extract the ZIP**:
   - Extract to a permanent location like `C:\Program Files\poppler`
   - You should have a folder structure like: `C:\Program Files\poppler\Library\bin\`

3. **Add to PATH**:
   ```powershell
   # Run PowerShell as Administrator
   [Environment]::SetEnvironmentVariable(
       "Path",
       $env:Path + ";C:\Program Files\poppler\Library\bin",
       [EnvironmentVariableTarget]::Machine
   )
   ```

4. **Verify Installation**:
   ```powershell
   # Restart PowerShell, then test:
   pdftoppm -v
   ```

## Option 2: Using Chocolatey (if you have it)

```powershell
choco install poppler
```

## Option 3: Manual PATH Configuration

If you don't want to use PowerShell:

1. Search for "Environment Variables" in Windows
2. Click "Environment Variables"
3. Under "System variables", find and select "Path"
4. Click "Edit"
5. Click "New"
6. Add: `C:\Program Files\poppler\Library\bin`
7. Click "OK" on all dialogs
8. **Restart your terminal/IDE**

## Verify It Works

After installation, restart your PowerShell and run:

```powershell
cd D:\Desktop\Insurance_Claim_Agent
.venv\Scripts\python.exe -c "from pdf2image import convert_from_path; print('Poppler is working!')"
```

If you see "Poppler is working!", you're all set!
